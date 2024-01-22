from django.contrib import admin
from .models import (
    LeagueMatches,
    Statistics,
    League,
    Player,
    Team,
    User
)

admin.site.register(LeagueMatches)
admin.site.register(Statistics)
admin.site.register(League)
admin.site.register(Player)
admin.site.register(Team)
admin.site.register(User)
