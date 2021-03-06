# coding: utf-8

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.core.mail import send_mail
from django.conf import settings
from django import forms
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit
from ..signals import contact_letter_sent
import logging
from django.contrib.auth.decorators import permission_required
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from captcha.fields import CaptchaField


class ContactLetterForm(forms.Form):

    from_email = forms.EmailField(
        label=_(u"Your Email Address"),
        required=True)

    subject = forms.CharField(
        label=_(u"Letter Subject"),
        max_length=128,
        required=True)

    message = forms.CharField(
        label=_(u"Letter text"),
        max_length=2560,
        widget=forms.Textarea,
        required=True)

    captcha = CaptchaField()

    def __init__(self, *args, **kwargs):
        super(ContactLetterForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_class = 'form-horizontal'
        self.helper.form_method = 'POST'
        self.helper.form_action = reverse('contact_letter')
        self.helper.help_text_inline = False
        self.helper.label_class = 'col-sm-4'
        self.helper.field_class = 'col-sm-7'
        self.helper.layout = Layout(
            Fieldset('', 'from_email', 'subject', 'message', 'captcha'),
            ButtonHolder(
                Submit('submit_button', _(u'Send')),
                Submit('cancel_button', _(u'Cancel'), css_class='btn-default')))


class ContactLetterView(FormView):
    template_name = 'contact_admin/contact_form.html'
    form_class = ContactLetterForm

    @method_decorator(permission_required('auth.add_user'))
    def dispatch(self, request, *args, **kwargs):
        return super(ContactLetterView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ContactLetterView, self).get_context_data(**kwargs)
        context['title'] = _(u"Contact Administrator")
        return context

    def form_valid(self, form):
        # send email
        subject = form.cleaned_data['subject']
        message = form.cleaned_data['message']
        from_email = form.cleaned_data['from_email']
        human = True
        try:
            send_mail(from_email + ' send me: ' + subject, message, settings.EMAIL_HOST_USER, [settings.ADMIN_EMAIL])
        except Exception:
            message = _(u"An error occurred during email transfer. Please, try again later.")
            message_error = '1'
            logger = logging.getLogger(__name__)
            logger.exception(from_email + _(u': error sending letter!'))
            return HttpResponseRedirect(u'%s?status_message=%s&message_error=%s' % (reverse('contact_admin'), message, message_error))
        else:
            message = _(u'Letter sent successfully!')
            contact_letter_sent.send(sender=self.__class__, email=from_email)
            return HttpResponseRedirect(u'%s?status_message=%s' % (reverse('contact_admin'), message))

    def post(self, request, *args, **kwargs):
        if request.POST.get('cancel_button'):
            return HttpResponseRedirect(u'%s?status_message=%s' % (reverse('contact_admin'), _(u'Letter sent canceled!')))
        else:
            return super(ContactLetterView, self).post(request, *args, **kwargs)


class ContactAdminView(TemplateView):
    template_name = 'contact_admin/contact_page.html'

    def get_context_data(self, **kwargs):
        context = super(ContactAdminView, self).get_context_data(**kwargs)
        context['contact_url'] = reverse('contact_admin')
        return context
