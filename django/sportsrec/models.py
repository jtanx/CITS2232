from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save, post_save, post_delete
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
import urllib, urllib2, json

class LocationManager(models.Manager):
    # Modification of http://goo.gl/cy5OUc
    def nearby_locations(self, latitude, longitude, radius, max_results=40):
        '''Determines all clubs within a set range, given in kilometres'''
        distance_unit = 6371
        if not latitude or not longitude:
            return self.filter(id_in=[])
        
        from django.db import connection, transaction
        from django.conf import settings
        import math
        cursor = connection.cursor()
        
        def acos(x):
            #print('acos(x)', x)
            if x is None: return None
            elif x <= -1: return math.pi
            elif x >= 1: return 0
            else: return math.acos(x)
        def cos(x):
            #print('cos(x)', x)
            if x is None: return None
            return math.cos(x)
        def radians(x):
            #print('radians(x)', x)
            if x is None: return None
            return math.radians(x)
        
        def sin(x):
            #print('sin(x)', x)
            if x is None: return None
            return math.sin(x)
        
        connection.connection.create_function('acos', 1, acos)
        connection.connection.create_function('cos', 1, cos)
        connection.connection.create_function('rad', 1, radians)
        connection.connection.create_function('sin', 1, sin)
     
        #Reference: 
        #http://janmatuschek.de/LatitudeLongitudeBoundingCoordinates
        latitude = math.radians(latitude)
        longitude = math.radians(longitude)
        r = 0.1570 / 1000 * radius # 0.1570 per 1000km
        latmin = latitude - r
        latmax = latitude + r
        deltaLong = math.asin(math.sin(r)/math.cos(latitude))
        lonmin = longitude - deltaLong
        lonmax = longitude + deltaLong
        
        if latmax > math.pi/2:
            latmax = -math.pi
            lonmin, lonmax = math.pi/2, math.pi
        if latmin < -math.pi/2:
            latmin, lonmin = -math.pi/2, -math.pi
            lonmax = math.pi
        if lonmin < -math.pi or lonmax > math.pi:
            lonmin, lonmax = -math.pi, math.pi
        
        #Old
        sql = \
        '''
        SELECT id, (6371 * acos(
          sin(rad(latitude))*sin(%s) +
          cos(rad(latitude))*cos(%s) * cos(rad(longitude) - %s)))
          AS distance
        FROM (
          SELECT id, latitude, longitude
          FROM sportsrec_club
          WHERE latitude IS NOT NULL AND longitude IS NOT NULL
        )
        WHERE distance < %d
        ORDER BY distance LIMIT 0, %d;
        ''' % (latitude, latitude, longitude, int(radius), max_results)
        
        sql2 = \
        '''
        SELECT id
          FROM sportsrec_club
          WHERE (rad(latitude) >= %f AND rad(latitude) <= %f) AND
                (rad(longitude) >= %f AND rad(longitude) <= %f) AND
                acos(sin(%f) * sin(rad(latitude)) + cos(%f) * cos(rad(latitude)) * cos (rad(longitude) - %f)) <= %f
          LIMIT 0, %d
        ''' % (latmin, latmax, lonmin, lonmax, latitude, latitude, longitude, r, max_results)

        cursor.execute(sql2)
        ids = [row[0] for row in cursor.fetchall()]

        return self.filter(id__in=ids)

class Member(models.Model):
    first_name = models.CharField(max_length=40)
    last_name = models.CharField(max_length=40)
    email = models.EmailField()
    address = models.CharField(max_length=255, blank=True, null=True)
    facebook = models.CharField(max_length=40, blank=True, null=True)
    twitter = models.CharField(max_length=40, blank=True, null=True)
    phone = models.CharField(max_length=40, blank=True, null=True)
    interests = models.CharField(max_length=255, blank=True, null=True)
    owner = models.ForeignKey(User)
    
    def __unicode__(self):
        return '%s %s (%s)' % (self.first_name, self.last_name, self.email)

class ClubTag(models.Model):
    name = models.CharField(max_length=40, unique=True)

    def __unicode__(self):
        return '%s' % (self.name)

class ClubType(models.Model):
    name = models.CharField(max_length=40, unique=True)
    description = models.CharField(max_length=255)
    club_count = models.IntegerField(default=0)
    
    @staticmethod
    def club_created(sender, instance, created, **kwargs):
        '''Auto increments the club count for a club type
           when a club is created'''
        if created and instance.type:
            instance.type.club_count += 1
            instance.type.save()

    @staticmethod
    def club_updated(sender, instance,  **kwargs):
        '''Auto updates club counts if a club type is changed'''
        if instance.pk:
            old_info = Club.objects.get(pk=instance.pk)
            if old_info.type != instance.type:
                if old_info.type:
                    old_info.type.club_count -= 1
                    old_info.type.save()
                if instance.type:
                    instance.type.club_count += 1
                    instance.type.save()

    @staticmethod
    def club_deleted(sender, instance, **kwargs):
        '''Auto updates club count when clubs are deleted'''
        try:
            instance.type.club_count -= 1
            instance.type.save()
        except ObjectDoesNotExist:
            #Club type was deleted...
            return

    def __unicode__(self):
        return '%s' % (self.name)

class Club(models.Model):
    name = models.CharField(max_length=40, unique=True)
    address = models.CharField(max_length=255)
    objects = models.Manager()
    #location = models.CharField(max_length=40, blank=True, null=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)
    location = LocationManager()
    
    tags = models.ManyToManyField(ClubTag, blank=True, null=True)
    type = models.ForeignKey(ClubType)
    member_count = models.IntegerField(default=0)
    created = models.DateField(default=datetime.now)
    recruiting = models.BooleanField(default=True)
    contact = models.ForeignKey(Member, blank=True, null=True,\
                                on_delete=models.SET_NULL,related_name='member_contact')
    description = models.CharField(max_length=255)
    facebook = models.CharField(max_length=40, blank=True, null=True)
    twitter = models.CharField(max_length=40, blank=True, null=True)
    owner = models.ForeignKey('Member',on_delete=models.SET_NULL, null=True, blank=True,\
                                related_name='member_owner')
    
    

    '''#Geocode on client side
    def save(self):
        if self.address:
            self.location = self.geocode(self.address)
        super(Club, self).save()
    
    def geocode(self, address):
        result = ''
        url = 'http://maps.googleapis.com/maps/api/geocode/json'
        params = urllib.urlencode({'address' : address, 'sensor' : 'false'})
        url = url + '?' + params
        response = urllib2.urlopen(url)
        try:
            vals = json.load(response)
        except ValueError:
            return result
        
        if 'results' in vals and len(vals['results']) > 0:
            loc = vals['results'][0]['geometry']['location']
            result = ",".join((str(loc['lat']), str(loc['lng'])))
        return result
    '''
    
    def __unicode__(self):
        return '%s' % (self.name)
  
'''  ???
class ClubMeta(models.Model):
    club = models.OneToOneField(Club)
    tags = models.ManyToManyField(ClubTag, blank=True, null=True)
    member_count = models.IntegerField(default=0)
    total_application_count = models.IntegerField(default=0)
    pending_application_count = models.IntegerField(default=0)
    recruiting = models.BooleanField(default=True)
''' 
    
class Membership(models.Model):
    joined = models.DateField(default=datetime.now)
    last_paid = models.DateField(blank=True, null=True)
    member = models.ForeignKey('Member')
    club = models.ForeignKey('Club')
    
    @staticmethod
    def membership_created(sender, instance, created, **kwargs):
        if created:
            instance.club.member_count += 1
            instance.club.save()

    @staticmethod
    def membership_deleted(sender, instance, **kwargs):
        try:
            instance.club.member_count -= 1
            instance.club.save()
        except ObjectDoesNotExist:
            #Club or member no longer exists.
            #As owner/contact is fk, they're nulled on member delete
            return
    
    class Meta:
        unique_together = (("member", "club"),)
    
    def __unicode__(self):
        return '%s belongs to %s' % (self.member, self.club)

class MembershipApplication(models.Model):
    applied = models.DateField(default=datetime.now)
    member = models.ForeignKey('Member')
    club = models.ForeignKey('Club')
    rejected = models.BooleanField(default=False)
    
    class Meta:
        unique_together = (("member", "club"),)
    
    def __unicode__(self):
        return '%s to %s' % (self.member, self.club)
        
class UserMeta(models.Model):
    #Needed? I dunno. maybe remove
    user = models.ForeignKey(User)
    member_count = models.IntegerField(default=0)
    membership_count = models.IntegerField(default=0)
    club_count = models.IntegerField(default=0)
'''
    @staticmethod
    def member_created(sender, instance, created, **kwargs):
        if created:
            meta, created = UserMeta.objects.get_or_create(user=instance.owner)
            meta.member_count += 1
            meta.save()

    @staticmethod
    def member_deleted(sender, instance, **kwargs):
        try:
            meta = UserMeta.objects.get(user=instance.owner)
        except ObjectDoesNotExist:
            return
        
        meta.member_count -= 1
        meta.save()

    @staticmethod
    def membership_created(sender, instance, created, **kwargs):
        if created:
            user = instance.member.owner
            meta, created = UserMeta.objects.get_or_create(user=user)
            meta.membership_count += 1
            meta.save()

    @staticmethod
    def membership_deleted(sender, instance, **kwargs):
        try:
            user = instance.member.owner
            meta = UserMeta.objects.get(user=user)
        except ObjectDoesNotExist:
            return

        meta.membership_count -= 1
        meta.save()

    @staticmethod
    def club_created(sender, instance, created, **kwargs):
        if created:
            meta, created = UserMeta.objects.get_or_create(user=instance.owner)
            meta.club_count += 1
            meta.save()

    @staticmethod
    def club_updated(sender, instance,  **kwargs):
        if instance.pk:
            old_info = Club.objects.get(pk=instance.pk)
            if old_info.owner != instance.owner:
                UserMeta.club_created(sender, instance, True)
                UserMeta.club_deleted(sender, old_info)

    @staticmethod
    def club_deleted(sender, instance, **kwargs):
        try:
            meta = UserMeta.objects.get(user=instance.owner)
        except ObjectDoesNotExist:
            return

        meta.club_count -= 1
        meta.save()
'''
#For club counting by type
post_save.connect(ClubType.club_created, sender=Club)
pre_save.connect(ClubType.club_updated, sender=Club)
post_delete.connect(ClubType.club_deleted, sender=Club)
#For membership tracking
post_save.connect(Membership.membership_created, sender=Membership)
post_delete.connect(Membership.membership_deleted, sender=Membership)
#For keeping track of user stats. May not be needed
'''post_save.connect(UserMeta.member_created, sender=Member)
post_delete.connect(UserMeta.member_deleted, sender=Member)
post_save.connect(UserMeta.membership_created, sender=Membership)
post_delete.connect(UserMeta.membership_deleted, sender=Membership)
post_save.connect(UserMeta.club_created, sender=Club)
pre_save.connect(UserMeta.club_updated, sender=Club)
post_delete.connect(UserMeta.club_deleted, sender=Club)'''
        
