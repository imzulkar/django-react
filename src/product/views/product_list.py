from django.views.generic import ListView
from django.core.paginator import Paginator
from django.db.models import Q
from product.models import (
    Variant,
    Product,
    ProductImage,
    ProductVariant,
    ProductVariantPrice,
)


class ProductListView(ListView):
    template_name = "products/list.html"
    model = Product
    context_object_name = "products"
    paginate_by = 10  # Adjust the number of products per page as needed

    def get_queryset(self):
        queryset = super().get_queryset()
        for product in queryset:
            product.images = ProductImage.objects.filter(product=product)
            product.variants = ProductVariant.objects.filter(product=product)
            product.variants.variant = Variant.objects.filter(
                id__in=list(product.variants.values_list("variant_id", flat=True))
            )
            for variant in product.variants:
                variant.prices = ProductVariantPrice.objects.filter(
                    Q(product_variant_one=variant)
                    | Q(product_variant_two=variant)
                    | Q(product_variant_three=variant)
                ).first()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = context["paginator"]
        page_numbers_range = 5  # Adjust the range of page numbers to show
        max_index = len(paginator.page_range)

        page = self.request.GET.get("page")
        current_page = int(page) if page else 1
        start_index = 0
        end_index = max_index
        if current_page > page_numbers_range:
            start_index = current_page - page_numbers_range
            end_index = current_page + page_numbers_range

        context["page_range"] = paginator.page_range[start_index:end_index]
        return context
