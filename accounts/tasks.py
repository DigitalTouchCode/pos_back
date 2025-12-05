from celery import shared_task
from utils.email import send_tenant_email
from .models import Invitation
from django.utils import timezone
from datetime import timedelta
from django.conf import settings

@shared_task
def send_invitation_email(invitation_id):
    invitation = Invitation.objects.get(id=invitation_id)
    send_tenant_email(
        tenant=invitation.tenant,
        subject=f"Invitation to join {invitation.tenant.name}",
        to_email=invitation.email,
        template_name='invitation',
        context={
            'invitation_url': f"{settings.FRONTEND_URL}/accept-invitation/{invitation.token}/",
            'inviter_name': f"{invitation.invited_by.first_name} {invitation.invited_by.last_name}",
            'role': invitation.role,
            'expiry_date': (timezone.now() + timedelta(days=7)).strftime("%B %d, %Y")
        }
    )