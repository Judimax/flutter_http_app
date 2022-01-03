from __main__ import app,db,ma,request,pprint,json,my_util,users,sqlalchemy
from users import User
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import text as sa_text
import uuid
from my_util import GUID

SQLALCHEMY_ECHO = True

class Cart(db.Model):
    cartId = db.Column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    cart = db.Column(db.String, nullable = False)
    total = db.Column(db.Float, nullable = False)

    def __init__(self, cart, total):
        self.cart = cart
        self.total = total

    def any(self):
        return '<cart cartId = {} ,quantity ={}, total={}>'.format(self.cartId, self.quantity,self.total)

class CartSchema(ma.Schema):
    class Meta:
        fields = ('cartId','cart','total')

cart_schema = CartSchema()
carts_schema = CartSchema(many=True)


@app.route('/cart/create',methods=['PUT'])
def create_cart():
    cartData = request.json['cartData']
    userData = request.json['userData']
    if(userData['user'] != None):

        newCart= Cart(
            cart =  json.dumps(cartData['cart']),
            total = cartData['total']
        )

        update_user_class = User.query.filter_by(user=userData['user']).first()
        if update_user_class is None:
            return {
                'message':{'message':'User not found'},
                'status':404
            }


        db.session.add(newCart)
        db.session.commit()

        cartId = newCart.cartId
        update_user_class.cartId = cartId
        db.session.flush()
        db.session.commit()
        return {

            'message':{
                'message':'Cart created successfully',
                'cartId':cartId
            }
        },200

@app.route('/cart/read',methods=['POST'])
def read_cart():
    data  = request.json['data']
    cart_id = data['cart_id']
    cart = Cart.query.filter_by(cartId=cart_id).first()
    if cart is None:
        return {
            'message':{'message':'Cart not found'},
            'status':404
        }
    cart.cart = json.loads(cart.cart)
    return {
        'message':{
            'message':'OK',
            'data':cart_schema.dump(cart)
        }
    },200


@app.route('/cart/update',methods=['PATCH'])
def update_cart():
    data = request.json['data']
    cart_id = data['cart_id']
    update_body = data['update_body']
    update_cart_class = Cart.query.filter_by(cartId=cart_id).first()
    if update_cart_class is None:
        return {
            'message':{'message':'Cart not found'},
        },404
    cart_to_update = cart_schema.dump(update_cart_class)
    cart_to_update["cart"] = json.loads(cart_to_update["cart"])
    cart_to_update = my_util.update_target(cart_to_update,update_body)

    update_cart_class.cart = json.dumps(cart_to_update["cart"])
    update_cart_class.total = cart_to_update["total"]
    db.session.flush()
    db.session.commit()
    return {
        'message':{
            'target':cart_to_update
        },

    },200

@app.route('/cart/delete',methods=['DELETE'])
def delete_cart():
    data  = request.json['data']
    cart_id = data['cart_id']
    cart = Cart.query.filter_by(cartId=cart_id).first()
    if cart is None:
        return {
            'message':{'message':'Cart not found'},
        },404
    db.session.delete(cart)
    db.session.commit()
    return {
        'message':{'message':'DELETED'},
    },200

@app.route('/cart/list',methods=['POST'])
def list_carts():
    carts = Cart.query.all()

    carts = [{
        'cartId':x.cartId,
        'cart':json.loads(x.cart),
        'total':x.total
    } for x in carts]
    return carts_schema.jsonify(carts)
    return {
        'status':200,
        'message':{
            'lists':carts_schema.jsonify(carts)
        }
    }

