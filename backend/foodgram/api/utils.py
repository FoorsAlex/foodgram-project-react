import io
import os

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from recipes.models import IngredientAmount
from django.db.models import F, Sum
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_shopping_cart_pdf(request):
    pdf = io.BytesIO()
    doc = SimpleDocTemplate(pdf)
    story = []
    styles = getSampleStyleSheet()
    styles['Normal'].fontName = 'DejaVuSerif'
    font_path = os.path.join(BASE_DIR, 'api/fonts/DejaVuSerif.ttf')
    pdfmetrics.registerFont(TTFont('DejaVuSerif', font_path, 'UTF-8'))
    shopping_list = IngredientAmount.objects.filter(
        recipe__shopping_cart_recipe__user=request.user).values(
        name=F('ingredient__name'),
        measurement_unit=F('ingredient__measurement_unit')
    ).annotate(total_amount=Sum('amount'))
    for i in shopping_list:
        ptext = (f'{i["name"]} '
                 f'({i["measurement_unit"]}) - {i["total_amount"]}')
        story.append(Paragraph(ptext, styles["Normal"]))
        story.append(Spacer(1, 12))
    doc.build(story)
    pdf.seek(0)
    return pdf
