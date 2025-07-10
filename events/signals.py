from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Event

@receiver(m2m_changed, sender=Event.participants.through)
def send_rsvp_email(sender, instance, action, pk_set, **kwargs):
    if action == 'post_add':
        # pk_set contains IDs of users added to participants
        from django.contrib.auth.models import User
        users = User.objects.filter(pk__in=pk_set)
        
        for user in users:
            subject = f"RSVP Confirmation for {instance.name}"
            message = (
                f"Hi {user.first_name or user.username},\n\n"
                f"Thank you for RSVPing to {instance.name}.\n"
                f"Date: {instance.date}\n"
                f"Time: {instance.time}\n"
                f"Location: {instance.location}\n\n"
                "We look forward to seeing you there!\n"
                "Best regards,\n"
                "Triple Events Team"
            )
            from_email = None
            recipient_list = [user.email]
            
            send_mail(subject, message, from_email, recipient_list)
