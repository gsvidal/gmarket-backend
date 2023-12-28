# Distinctiveness and Complexity

The detailed description bellow demonstrates the complexity of my e-commerce application, showcasing over three years of accumulated web development expertise. In my pursuit of excellence, I opted for a challenging project, steering away from the simplicity of a basic Django React JS application. This deliberate choice reflects my commitment to meeting course requirements and building a project that meets industry standards.

## Gmarket is an e-commerce fullstack app with some CMS(Content Management System) functionalities, it's been built with:

Backend:

- Python
- Django (Python framework)

Database:

- SQL (I'll use Postgresql in production for being a more reliable and robust option)

## File's Content

Backend and Database:

- The models.py file contains a custom user model (User) inheriting from Django's AbstractUser, models for sellers (Seller) and customers (Customer), a model for product categories (Category), and a model for individual products (Product). These models establish relationships between users, products, and categories, providing a foundation for a comprehensive e-commerce system.

- The urls.py file contains the urlpatterns list that defines various URL patterns for all the views in my Django app.

- The views.py contains all the views that facilitates user registration, login, and product management in an e-commerce application. With role-based authentication, the system supports both sellers and customers. User registration involves validation and token creation. The seller dashboard displays paginated products, and categories are accessible with proper role authorization. Product creation includes comprehensive input validation, considering image size and format. The application handles product retrieval, deletion, and updates, ensuring a structured and secure e-commerce experience with Django's ORM and JsonResponse for efficient JSON communication.

## Application functionalities/features

- Users can login.
- Users can logout.
- Users can register with different roles: Seller or Customer.
- If username already exists the user will be notified with an error message.
- Depending on each of those user will have different permissions and clearance (in the front and back).
- Seller users can create a product and add name, brand, description, base price, price, stock, image (as jpg, png or jpeg) formats, and a category dropdown list.
- Only the last two (image and category) are optional, the rest are required fields.
- If a seller user doesn't meet the conditions for any field when filling them out an error message will be shown in the create product modal. (The error text comes from the back and it's caught in the frontend if something goes wrong).
- Seller can cancel or create the product.
- If seller user add the product(a http post request will be sent to the backend), if creation is successful, the product will be shown in their Dashboard menu.
- When navigating to Dashboard menu, seller user can view their products and edit them or delete them.
- When user click on edit a edit product form will be rendered and will ask for new data showing the previous data at first.
- Seller user can also delete a product, when click on delete(DELETE http request), and if it's sucessfully deleted, the item will disappear with a fading animation.
- When user clicks on delete button a similar modal will be shown with a confirmation message.
- In case of user chose the customer role, won't have access to the dashboard, but will have the permission to add products to their shopping cart.
- There's Pagination (front & back), in the client will show previous, next buttons as well as some page numbers or elipsis in case the total pages are greater than or equal to the max amount of visible pages (5).
- There's also a products-per-page filter with set values (5,10,15,25 and 50) products/page.
- These values will change the size of the pagination (a low products-per-page will result in a larger pagination pages buttons and viceversa).
- Responsiveness is implemented with flexible container and products row sizes and header with a hamburger menu
- Glassy effects for Header, hamburger menu and modals.
- Dark mode by default.
- Modern theming and styling that makes the app more homogeneous and visually appealing.

In summary, I've implemented all CRUD operations and error handling both in client (frontend) and server (backend) side.

## Installation and starting backend and front dev servers

Install the project:

`git clone -b web50/projects/2020/x/capstone git@github.com:me50/gsvidal.git`

To run locally:
Open a new terminal and run:

`cd gsvidal`

Install a virtual environment:

`python -m venv .venv`

After the .venv file is created, activate it running:

`cd .venv/`

`source ./Scripts/activate && cd ..`

Install all the dependencies

`pip install -r requirements.txt`

Make the migrations for the cmscommerce app:

`python manage.py makemigrations cmscommerce`

Migrate them.

`python manage.py migrate`

Create categories manually:

`python manage.py shell`

Copy and paste:

```
from cmscommerce.models import Category

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
```

Start the development server:

`python manage.py runserver`

The backend development server will start by default at http://127.0.0.1:8000/