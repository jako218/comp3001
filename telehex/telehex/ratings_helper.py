#coding: utf-8

from django import template
import math
register = template.Library()

@register.filter
def to_num_hex(rating):
	spans = ""
	solid_hex = int(math.floor(rating/2))
	for i in range(solid_hex):
		spans += "⬣"
	return spans
