import itertools
from django_filters import rest_framework as filters
from django.db.models import Q
from inventory.models import Variant


class VariantFilter(filters.FilterSet):
    sku = filters.CharFilter(method='sku_filter')
    product = filters.CharFilter(method='get_variant_of_product')

    class Meta:
        model = Variant
        fields = ["sku", "product"]
    
    def sku_filter(self, queryset, name, value):
        combinations = []
        value = [value for value in value.split(' ') if value]
        for r in range(len(value)+1):
            for words in itertools.combinations(value, r):
                combinations.append(words)

        sku_word_list = []

        for combination in combinations:
            sku_list = []

            for word in combination:
                sku_list.append(word)
            sku_word = '_'.join(sku_list)
            sku_word_list.append(sku_word)
        q= Q()
        for word in sku_word_list[1:]:
            qs = Q(sku__icontains=word)
            q |= qs
        return queryset.filter(q)
    
    def get_variant_of_product(self, queryset, name, value):
        return queryset.filter(product__uuid=value)