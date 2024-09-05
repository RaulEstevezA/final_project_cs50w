## Autor: Raul Estevez
### GitHub profile: [RaulEstevezA](https://github.com/RaulEstevezA)
### LinkedIn: [Raul Estevez](https://www.linkedin.com/in/raul-estevez-abella-9a2a1687/)
### Contact: [r.estevezbella@gmail.com](mailto:r.estevezbella@gmail.com)

[Link to demo video](https://youtu.be/ckqKTbNd3lc)

# CAPSTONE - DuckyWare
## Final Project of the CS50w Course

### BRIEF INTRODUCTION AND WHY I CHOSE IT

Having taken more courses on the CS50 platform, I started thinking about an idea for my final project from the beginning. Among all the projects I could undertake, I wanted to create one that could realistically help me get a job in the future, a project that you might encounter in your professional life. All my thoughts were focused on the world of online sales, which seemed the most sensible to me. Within online sales, I focused on selling hardware, a sector I quite like.

I created a fully functional online product sales website that is more minimalist than what you usually find. Many current sites offer a saturation of information that ends up driving away less experienced users. I wanted it to be a pleasant page for any type of person.

For the name and theme, I was inspired by the rubber duck shown so often in CS50 courses, hence the constant yellow color on the website and its name: DuckyWare, a mix of "duck" and "hardware."

### REQUIREMENTS

**Why is it different from Project 2?**
Project 2 (commerce) was a basic project that presented sales listings like auctions, very similar to eBay. It was organized into categories, had a user who owned the sale, a watchlist, and an ad creation page.

Although it is true that my online store project uses Watchlist and Categories, I consider it something that an online sales page must necessarily have. That is the only similarity they have.

DuckyWare is an advanced e-commerce platform developed with Django on the backend and JavaScript on the frontend, Bootstrap for a large part of the styling, and designed to be highly functional and scalable. The application offers a robust set of features that enable a complete online shopping experience. This web application not only allows users to purchase computer components and peripherals but also offers an intuitive and responsive user interface that works optimally on mobile devices.

It offers a dynamic homepage fetching randomly featured products, best-selling products, and a selection of last units in stock, the latter two calculated in real time. The category system is dynamically loaded from the database, allowing hierarchical and organized navigation that also adapts to possible changes by adding new categories or subcategories. There is also product catalog management, shopping cart functionality, order processing, and integration with PayPal for payments or a top bar search system that offers dynamic search by product titles and displays them on a results page.

### DISTINCTIVENESS AND COMPLEXITY

**Distinctiveness**

DuckyWare is clearly distinguished from other course projects due to its comprehensive approach and modular architecture. Unlike the basic e-commerce project based on eBay, my project implements a complete system of categories and subcategories, inventory management, discounts, and advanced search, making it much more robust and complex.

**Highlighted Features:**

- **Category and Subcategory System:** Implementation of nested categories allowing hierarchical organization of products.
- **Advanced Cart and Order Management:** Cart functionality includes complex discount logic, stock management, and real-time updates. Orders are processed with detailed item tracking and order status management.
- **Dynamic Discounts:** Handling discounts and discounted units for each product, adding an additional layer of business logic.
- **Advanced Search:** Search functionality that allows users to search for products by title, integrating search with corresponding images for an enhanced user experience.
- **Detailed Product Visualization:** Detailed product visualization page that shows all images associated with each product and allows users to see specific details of each product in an organized format.
- **Dynamic JavaScript:** Use of JavaScript to enhance user interaction, including dynamic loading of page-specific scripts to improve performance and code modularity.
- **Profile Management:** Users can update their profile information, including shipping addresses and contact details, directly from the application.

**Complexity**

The backend is built with Django with complex interactions with the database to manage product categories, orders, and users.
JavaScript is used to enhance the user experience with dynamic cart updates, real-time validations, and AJAX requests for smooth transitions without reloading the page.
In terms of security, CSRF protection practices have been implemented.

### File Structure

- **media:** Directory containing images of uploaded products.
- Inside **store/**:
  - **models.py:** Defines the data models, including categories, products, and user profiles.
  - **static:** Contains static files like CSS and JavaScript.
  - **templates:** Contains HTML templates for the different pages of the application.
  - **templetags:** Adds additional functionalities.
  - **product_types.py:** Centralizes the definitions of product models and their mapping to categories.
  - **urls.py:** Configures URL routes for site navigation.
  - **views.py:** Contains Django views that handle backend logic.

### Required Resources

To run the application, you need Python with Django and the following two packages:
- Pillow (`pip install Pillow`)
- paypalrestsdk (`pip install paypalrestsdk`)

### How to Run

Install the packages mentioned in `requirements.txt` and initialize in the console:
```sh
python manage.py runserver
