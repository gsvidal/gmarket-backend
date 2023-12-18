# Script to run back dev server

cd backend/gmarket/.venv/
source ./Scripts/activate && cd ..
python manage.py runserver
cd sffdf


# Create product categories
from cmscommerce.models import Category

# Create a new category
category1 = Category(name='Technology', code='tech')
category2 = Category(name='Fashion', code='fashion')
category3 = Category(name='Grocery', code='grocery')
category4 = Category(name='Books', code='books')
category5 = Category(name='Music', code='music')
category6 = Category(name='Sports', code='sports')
category7 = Category(name='Games', code='games')
category8 = Category(name='No Category', code='no-category') 

category1.save()
category2.save()
category3.save()
category4.save()
category5.save()
category6.save()
category7.save()
category8.save()