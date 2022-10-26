from flask import Flask, render_template, redirect, url_for, flash, send_file, request, session
from io import BytesIO
import base64
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_required, logout_user, LoginManager, login_user, current_user
from sqlalchemy.orm import relationship
from forms import AddProductForm, LoginForm, Register
from flask_bcrypt import Bcrypt, generate_password_hash, check_password_hash

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config['SECRET_KEY'] = "0532a2b15fe532dd17fe9344"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# DATABASE
class User(db.Model, UserMixin):
    __table__name = 'user'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False, unique=False)
    last_name = db.Column(db.String(50), nullable=False, unique=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False, unique=True)
    image = db.Column(db.String, nullable=False, unique=False)
    products = relationship("Product", back_populates="owner")


class Product(db.Model):
    __table__name = 'product'
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    owner = relationship("User", back_populates="products")
    item_name = db.Column(db.String(50), nullable=False, unique=False)
    description = db.Column(db.Text, nullable=False, unique=False)
    item_photo = db.Column(db.String, nullable=False, unique=False)
    price = db.Column(db.Integer, nullable=False, unique=False)


# db.create_all()


def merge_dictionary(dict1, dict2):
    if isinstance(dict1, list) and isinstance(dict2, list):
        return dict1 + dict2
    elif isinstance(dict1, dict) and isinstance(dict2, dict):
        return dict(list(dict1.items()) + list(dict2.items()))
    return False


@app.route("/")
@app.route("/home")
def home():
    product = db.session.query(Product).all()
    return render_template("index.html", items=product)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = Register()
    if User.query.filter_by(email=form.email.data).first():
        flash("This account exist, login instead")
        return redirect(url_for('login'))
    if form.validate_on_submit():
        new_user = User(first_name=form.f_name.data, last_name=form.l_name.data, email=form.email.data,
                        password=generate_password_hash(password=form.password.data),
                        image=form.photo.data.read())
        db.session.add(new_user)
        db.session.commit()
        login_user(user=new_user)
        return redirect(url_for('home'))
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f"An error occurred: {err_msg}")
    return render_template("register.html", form=form, current_user=current_user)


@app.route("/login", methods=["POST", "GET"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = db.session.query(User).filter_by(email=email).first()
        print(user)
        if not user:
            flash("You don't have an account yet, please register")
            return redirect(url_for("register"))
        elif not check_password_hash(password=password, pw_hash=user.password):
            flash("Incorrect Password, try again")
            return redirect(url_for("login"))
        else:
            login_user(user=user)
            flash("Success")
            return redirect(url_for("home"))
    return render_template("login.html", form=form, current_user=current_user)


@app.route('/add-product', methods=['GET', 'POST'])
@login_required
def add_products():
    form = AddProductForm()
    if form.validate_on_submit():
        product = Product(item_name=form.item_name.data, description=form.description.data, price=form.price.data,
                          item_photo=form.item_photo.data)
        db.session.add(product)
        db.session.commit()
        flash("You Successfully Added A Product")
        return redirect(url_for('home'))
    return render_template('add-products.html', form=form)


@app.route("/product/info/<int:product_id>", methods=["GET", "POST"])
@login_required
def product_info(product_id):
    details = Product.query.filter_by(id=product_id)
    return render_template("info.html", details=details)


@app.route("/cart", methods=["GET", "POST"])
@login_required
def add_cart():
    try:
        product_id = request.args.get("item_id")
        product = Product.query.filter_by(id=product_id).first()
        if product_id:
            DictItems = {product_id: {"name": product.item_name, "price": product.price, "photo": product.item_photo}}
            if "ShoppingCart" in session:
                print(session["ShoppingCart"])
                if product_id in session["ShoppingCart"]:
                    flash("You have this product already")
                else:
                    session["ShoppingCart"] = merge_dictionary(session["ShoppingCart"], DictItems)
                    return redirect(request.referrer)
            else:
                session["ShoppingCart"] = DictItems
                return redirect(request.referrer)
    except Exception as e:
        print(e)
    finally:
        return redirect(request.referrer)


@app.route('/logout')
def logout():
    logout_user()
    flash("Thank you for Shopping")
    return redirect(url_for('home', current_user=current_user))


if __name__ == '__main__':
    app.run(debug=True)
