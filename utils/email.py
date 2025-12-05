from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def send_tenant_email(tenant, subject, to_email, template_name, context=None, from_email=None):
    if context is None:
        context = {}
    
    if 'tenant' not in context:
        context['tenant'] = tenant
    
    html_message = render_to_string(f'emails/{template_name}.html', context)
    text_message = strip_tags(html_message)

    from_email = from_email or f'"{tenant.name}" <{tenant.email_from}>'

    email = EmailMultiAlternatives(
        subject=subject, 
        body=text_message, 
        from_email=from_email, 
        to=[to_email],
        connection=tenant.get_email_connection()
    )
    email.attach_alternative(html_message, 'text/html')
    
    return email.send(fail_silently=False)
