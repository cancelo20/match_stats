from django.contrib import admin
from .models import (
    LeagueMatches,
    Statistics,
    IsUpdating,
    League,
    Player,
    Team
)

admin.site.register(LeagueMatches)
admin.site.register(Statistics)
admin.site.register(IsUpdating)
admin.site.register(League)
admin.site.register(Player)
admin.site.register(Team)
