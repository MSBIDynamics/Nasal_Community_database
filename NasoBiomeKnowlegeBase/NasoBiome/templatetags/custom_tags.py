from django import template

register = template.Library()

@register.inclusion_tag('components/stats_card.html')
def stats_card(title, value, icon_name, change_text=None, change_icon_name=None, icon_bg_class="bg-blue-100 dark:bg-blue-500/20", change_span_class="bg-success-50 text-success-600 dark:bg-success-500/15 dark:text-success-500"):
    """
    Renders a statistics card for the dashboard.
    This tag takes several arguments and renders the 'components/stats_card.html'
    template with them.
    """
    return {
        'title': title,
        'value': value,
        'icon_name': icon_name,
        'change_text': change_text,
        'change_icon_name': change_icon_name,
        'icon_bg_class': icon_bg_class,
        'change_span_class': change_span_class,
    }

@register.inclusion_tag('components/data_table_card.html')
def data_table_card(title, headers, rows, see_all_url=None):
    """
    Renders a card with a dynamic data table.
    - title: The main heading for the card (e.g., "Recent Orders").
    - headers: A list of strings for the table headers.
    - rows: A list of dictionaries, where each dict represents a row.
    - see_all_url: An optional URL for the "See all" button.
    """
    return {
        'title': title,
        'headers': headers,
        'rows': rows,
        'see_all_url': see_all_url,
    }
