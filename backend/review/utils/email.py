from django.conf import settings
from review.models import ReviewRole
from django.template.loader import get_template
from django.core.mail import EmailMessage


def send_review_version_email(user, data):
    is_dev = settings.BUGSNAG.get('release_stage') == 'development'

    # email data
    email = {
        'subject': '[LPDR Data Almanac] Ready for review',
        'to': [],
        'bcc': []
    }

    role = data['info'].replace(' Review', '')
    if role in ['Upload DD', 'Grantee'] + settings.DA_REVIEW_ROLES:
        # create the send to list
        if role == 'Grantee' or role == 'Upload DD':
            email['to'].append(data['review'].user.email)
        else:
            roles = ReviewRole.objects.filter(role=role)
            for db_role in roles:
                email['to'].append(db_role.user.email)

        if is_dev:
            # append original to to message
            original_to = email['to']
            email['to'] = [settings.REVIEW_CONTACT_EMAIL]
            email['bcc'] = []
        else:
            original_to = None
            email['bcc'] = [settings.REVIEW_CONTACT_EMAIL]

        # build the data for the message
        ctx = {
            'user': user,
            'original_to': original_to,
            'user_type': role,
            'review': data['review'],
            'url': settings.APP_URL
        }

        send_message('review_ready.html', email, ctx)


def send_review_completed_email(user, data):
    is_dev = settings.BUGSNAG.get('release_stage') == 'development'

    # email data
    email = {
        'subject': '[LPDR Data Almanac] Review completed',
        'to': [],
        'bcc': []
    }

    # fetch all admin roles
    roles = ReviewRole.objects.filter(role=settings.DA_REVIEW_ADMIN_ROLE)
    for db_role in roles:
        email['to'].append(db_role.user.email)

    if is_dev:
        # append original to to message
        original_to = email['to']
        email['to'] = [settings.REVIEW_CONTACT_EMAIL]
        email['bcc'] = []
    else:
        original_to = None
        email['bcc'] = [settings.REVIEW_CONTACT_EMAIL]

    # build the data for the message
    ctx = {
        'user': user,
        'original_to': original_to,
        'user_type': settings.DA_REVIEW_ADMIN_ROLE,
        'review': data.review,
        'url': settings.APP_URL
    }

    send_message('review_complete.html', email, ctx)


def send_review_removal_email(user, review):
    is_dev = settings.BUGSNAG.get('release_stage') == 'development'

    # email data
    email = {
        'subject': '[LPDR Data Almanac] Request review removal',
        'to': [],
        'bcc': []
    }

    # fetch all admin roles roles
    roles = ReviewRole.objects.filter(role=settings.DA_REVIEW_ADMIN_ROLE)
    for db_role in roles:
        email['to'].append(db_role.user.email)

    if is_dev:
        # append original to to message
        original_to = email['to']
        email['to'] = [settings.REVIEW_CONTACT_EMAIL]
        email['bcc'] = []
    else:
        original_to = None
        email['bcc'] = [settings.REVIEW_CONTACT_EMAIL]

    # build the data for the message
    ctx = {
        'user': user,
        'original_to': original_to,
        'user_type': settings.DA_REVIEW_ADMIN_ROLE,
        'review': review,
        'url': settings.APP_URL
    }

    send_message('review_removal.html', email, ctx)


def send_message(template, email, context):
    # build and send the email
    message = get_template(template).render(context)
    email_message = EmailMessage(email['subject'], message, to=email[
                                 'to'], bcc=email['bcc'])
    email_message.content_subtype = 'html'
    email_message.send()
