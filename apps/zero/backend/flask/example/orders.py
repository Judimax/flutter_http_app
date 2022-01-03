from __main__ import app,db,ma,request,pprint,json,my_util,users,cart
from users import User
from cart import Cart
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import text as sa_text
import uuid
from my_util import GUID




class Order(db.Model):
    orderId =db.Column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    user = db.Column(db.String(50),  nullable=False)
    cart  = db.Column(db.String(),   nullable=False)  # a string list
    billing = db.Column(db.String()) # a string dict
    shipping = db.Column(db.String()) # a string dict
    total = db.Column(db.Float(), nullable=False)

    def __init__(self, user, cart, billing, shipping,total,orderId):
        self.user = user
        self.cart = cart
        self.billing = billing
        self.shipping = shipping
        self.total = total
        self.orderId = orderId

    def any(self):
        return '<order orderId = {}, user = {} cart = {} billing = {} shipping ={} total ={}'.format(
            self.orderId,
            self.user,
            json.loads(self.cart),
            json.loads(self.billing),
            json.loads(self.shipping),
            self.total
        )

class OrderSchema(ma.Schema):
    class Meta:
        fields = ('orderId', 'user', 'cart', 'billing', 'shipping','total')

order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)


@app.route('/order/create',methods=['PUT'])
def create_order():
    data = request.json['data']
    newOrder = Order(
        data['user'],
        json.dumps(data['cart']),
        json.dumps(data['billing']),
        json.dumps(data['shipping']),
        data['total'],
        None
    )
    db.session.add(newOrder)
    db.session.commit()
    return {
        'message':{
            'message':'CREATED',
            'orderId':newOrder.orderId
        },

    },201


@app.route('/order/read',methods=['POST'])
def read_order():
    data = request.json['data']
    orderId = data['orderId']
    order = Order.query.filter_by(orderId=orderId).first()
    if  order is None:
        return {
            'message':{'message':'NOT FOUND'}
        },404
    else:
        order.cart = json.loads(order.cart)
        order.billing = json.loads(order.billing)
        order.shipping = json.loads(order.shipping)
        return {
            'message':{
                'message':'OK',
                'data':order_schema.dump(order)
            }
        }

@app.route('/order/update',methods=['PATCH'])
def update_order():
    data = request.json["data"]
    update_id = data['orderId']
    update_body = data["update_body"]
    update_class = Order.query.filter_by(orderId=update_id).first()
    if update_class is None:
        return {
            'message':{'message':'NOT FOUND'}
        },404
    target_to_update = order_schema.dump(update_class)
    target_to_update["cart"] =  json.loads(target_to_update["cart"])
    target_to_update["billing"] =  json.loads(target_to_update["billing"])
    target_to_update["shipping"] = json.loads(target_to_update["shipping"])
    target_to_update = my_util.update_target(target_to_update,update_body)

    update_class.user = target_to_update["user"]
    update_class.total = target_to_update["total"]
    update_class.cart = json.dumps(target_to_update["cart"])
    update_class.billing = json.dumps(target_to_update["billing"])
    update_class.shipping = json.dumps(target_to_update["shipping"])
    db.session.flush()
    db.session.commit()
    return{
        'message':{
            'target':target_to_update,
        }
    },200


@app.route('/order/adminUpdate',methods=['PATCH'])
def admin_update_order():
    data = request.json["data"]
    update_id = data['orderId']
    update_body = data["update_body"]
    update_class = Order.query.filter_by(orderId=update_id).first()
    if update_class is None:
        return {
            'message':{'message':'NOT FOUND'}
        },404
    target_to_update = order_schema.dump(update_class)

    def dict_to_str(x):
        target_to_update[x] = json.loads(target_to_update[x])
    [ dict_to_str(x) for x in ["cart","billing","shipping"]]
    target_to_update = my_util.update_target(target_to_update,update_body)


    def target_class_update(attr,val,idx):
        if idx >= 2:
            setattr(update_class,attr,json.dumps(val))
        else:
            setattr(update_class,attr, val)

    [
        target_class_update(x,target_to_update[x],i)
        for i,x in enumerate(["user","total","cart","billing","shipping"])
    ]
    db.session.flush()
    db.session.commit()
    return{
        'message':{
            'target':target_to_update,
        }
    },200


@app.route('/order/delete',methods=['DELETE'])
def delete_order():
    data = request.json['data']
    order = Order.query.filter_by(orderId=data['orderId']).first()
    if order is None:
        return {
            'message':{'message':'NOT FOUND'}
        },404
    else:
        db.session.delete(order)
        db.session.commit()
        return {
            'message':{'message':'DELETED'}
        },200

@app.route('/order/adminDelete',methods=['DELETE'])
def admin_delete_order():
    data = request.json['data']
    order = Order.query.filter_by(orderId=data['orderId']).first()
    if order is None:
        return {
            'message':{'message':'NOT FOUND'}
        },404
    else:
        db.session.delete(order)
        db.session.commit()
        return {
            'message':{'message':'DELETED'}
        },200

@app.route('/order/list',methods=['POST'])
def list_orders():

    data = request.json.get('data',{})
    my_filter = data.get('filter',[])
    pages = data.get('pages') or {
        'page':0,
        'per_page':20
    }

    # max per_page is 100
    if pages['per_page'] > 100:
        pages['per_page'] = 100
    #
    start = pages['page']* pages['per_page']
    stop = (pages['page']+1)* pages['per_page']
    items = orders_schema.jsonify(Order.query.slice(start, stop).all()).json


    # filter according to the query
    if my_filter is not None:
        for x in items:
            for y in my_filter:
                del x[y]
    #
    #

    items = [ {
        **x,
        **{ y:json.loads(x[y]) if x[y] is not None else None for y in ['cart','billing','shipping']},

    } for x in items]

    return{
        'message':{
            'list':items
        }
    }, 200

