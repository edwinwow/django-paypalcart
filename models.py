import datetime

from django.conf import settings
from django.db import models
from django.contrib import auth
from django.utils.translation import ugettext as _, ungettext, ugettext_lazy
from django.contrib.auth.models import User

from cartridge.shop.models import Product

import signals
import utils


_recurrence_unit_days = {
    'D': 1.,
    'W': 7.,
    'M': 30.4368,                      # http://en.wikipedia.org/wiki/Month#Julian_and_Gregorian_calendars
    'Y': 365.2425,                     # http://en.wikipedia.org/wiki/Year#Calendar_year
    }

_TIME_UNIT_CHOICES = (
    ('0', ugettext_lazy('No trial')),
    ('D', ugettext_lazy('Day')),
    ('W', ugettext_lazy('Week')),
    ('M', ugettext_lazy('Month')),
    ('Y', ugettext_lazy('Year')),
    )

class Subscription(Product):
    trial_period = models.PositiveIntegerField(null=True, blank=True)
    trial_unit = models.CharField(max_length=1, null=True, choices=_TIME_UNIT_CHOICES)
    recurrence_period = models.PositiveIntegerField(null=True, blank=True)
    recurrence_unit = models.CharField(max_length=1, null=True,
                                       choices=((None, ugettext_lazy("No recurrence")),)
                                       + _TIME_UNIT_CHOICES)

    _PLURAL_UNITS = {
        '0': ugettext_lazy('No trial'),
        'D': 'days',
        'W': 'weeks',
        'M': 'months',
        'Y': 'years',
        }



# add User.get_subscription() method
def __user_get_subscription(user):
    if not hasattr(user, '_subscription_cache'):
        sl = Subscription.objects.filter(group__in=user.groups.all())[:1]
        if sl:
            user._subscription_cache = sl[0]
        else:
            user._subscription_cache = None
    return user._subscription_cache
auth.User.add_to_class('get_subscription', __user_get_subscription)


class ActiveUSManager(models.Manager):
    """Custom Manager for UserSubscription that returns only live US objects."""
    def get_query_set(self):
        return super(ActiveUSManager, self).get_query_set().filter(profile_status=3)

_STATUS_CHOICES = {
    "1": 'Cancelled',
    "2": 'Suspended',
    "3": 'Active'
    "4": 'Deleted',
    }

class SubscriptionProfile(models.Model):
    user = models.ForeignKey("auth.User")
    subscription = models.ForeignKey(Subscription)
    paypal_profile_id = models.CharField(max=15, null=False, blank=False, unique=True)
    paypal_profile_status = models.PositiveIntegerField(null=False, blank=False, choices=_STATUS_CHOICES)
    
    objects = models.Manager()
    active_objects = ActiveUSManager()

    grace_timedelta = datetime.timedelta(
        getattr(settings, 'SUBSCRIPTION_GRACE_PERIOD', 2))

    class Meta:
        unique_together = (('user', 'subscription'), )


    def cancel(self):
        """Unsubscribe user."""
        self.paypal_profile_status = 1
        self.save()

    def suspend(self):
        """Subscribe user."""
        self.paypal_profile_status =2
        self.save()
        
    def active(self):
        """Unsubscribe user."""
        self.paypal_profile_status = 3
        self.save()
        
    def delete(self):
        """Unsubscribe user."""
        self.paypal_profile_status = 4
        self.save()


    @models.permalink
    def get_absolute_url(self):
        return ('subscription_usersubscription_detail', (), dict(object_id=str(self.id)))

    def __unicode__(self):
        rv = u"%s's %s" % (self.user, self.subscription)
        if self.expired():
            rv += u' (expired)'
        return rv




