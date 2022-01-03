from __main__ import app,db,ma,request,pprint,json,my_util
from my_util import GUID


class User(db.Model):
    user = db.Column(db.String(200), primary_key=True)
    myPass = db.Column(db.String(200),unique=True, nullable=False)
    billing = db.Column(db.String())
    shipping = db.Column(db.String())
    shipping_same_as_billing = db.Column(db.Boolean)
    cartId = db.Column(GUID(), nullable=True)
    orderId = db.Column(db.String(), nullable=True,default = lambda:json.dumps([])) # list of orderId's

    def __init__ (self, user, myPass, billing, shipping, shipping_same_as_billing):
        self.user = user
        self.myPass = myPass
        self.billing = billing
        self.shipping = shipping
        self.shipping_same_as_billing = shipping_same_as_billing


    def any(self):
        return '<user user = {} ,myPass ={}, billing={}, shipping={}, shipping_same_as_billing={}, cartId={}, orderId={}>'.format(
            self.user,
            self.myPass,
            self.billing,
            self.shipping,
            self.shipping_same_as_billing,
            self.cartId,
            self.orderId
        )


class UserSchema(ma.Schema):
    class Meta:
        fields = ('user','myPass','billing', 'shipping', 'shipping_same_as_billing','cartId','orderId')

user_schema = UserSchema()
users_schema = UserSchema(many=True)


@app.route('/users/create',methods=['PUT'])
def create_user():
    data = request.json['data']
    newUser = User(
        data['user'],
        data['pass'],
        json.dumps(data['billing']),
        json.dumps(data['shipping']),
        data['shipping']['sameAsBilling']['checked']
    )
    db.session.add(newUser)
    db.session.commit()
    return {
        'message':{'message':'CREATED'},

    },201



@app.route('/users/read',methods=['POST'])
def read_user():
    data = request.json['data']
    user =   data['user']
    mYpass = data['pass']
    my_filter = data['filter'] or None
    user = User.query.filter_by(user=user).first()
    if user is None:
        return {
            'message':{'message':'User not found'},

        },404
    elif user.myPass == mYpass:
        user.billing = json.loads(user.billing)
        user.shipping = json.loads(user.shipping)
        user.orderId = json.loads(user.orderId)
        return_data = user_schema.dump(user)
        if my_filter is not None:
            filter_data = {}
            for x in my_filter:
                filter_data[x] = return_data[x]
            return_data = filter_data
        return {
            'message':{
                'message':'OK',
                'data':return_data
            },

        },200


@app.route('/users/update',methods=['PATCH'])
def update_user():
    # needs authentication before update
    data = request.json["data"]
    user = data['user']
    update_body = data['update_body']
    update_user_class = User.query.filter_by(user=user).first()

    if update_user_class is None:
        return {
            'message':{'message':'User not found'},
        },404
    user_to_update = user_schema.dump(update_user_class)
    user_to_update["billing"] =  json.loads(user_to_update["billing"])
    user_to_update["shipping"] = json.loads(user_to_update["shipping"])
    user_to_update["orderId"] = json.loads(user_to_update["orderId"])
    user_to_update =  my_util.update_target(user_to_update,update_body)


    update_user_class.user = user_to_update["user"]
    update_user_class.myPass = user_to_update["myPass"]
    update_user_class.billing = json.dumps(user_to_update["billing"])
    update_user_class.shipping = json.dumps(user_to_update["shipping"])
    update_user_class.orderId = json.dumps(user_to_update["orderId"])
    update_user_class.shipping_same_as_billing = user_to_update["shipping_same_as_billing"]

    db.session.flush()
    db.session.commit()
    return {
        'message':{
            'target':user_to_update
        },

    },200


@app.route('/users/adminUpdate',methods=['PATCH'])
def admin_update_user():
    # needs admin authentication before update
    data = request.json["data"]
    user = data['user']
    update_body = data['update_body']
    update_user_class = User.query.filter_by(user=user).first()

    if update_user_class is None:
        return {
            'message':{'message':'User not found'},
        },404
    user_to_update = user_schema.dump(update_user_class)
    user_to_update["billing"] =  json.loads(user_to_update["billing"])
    user_to_update["shipping"] = json.loads(user_to_update["shipping"])
    user_to_update["orderId"] = json.loads(user_to_update["orderId"])
    user_to_update =  my_util.update_target(user_to_update,update_body)


    update_user_class.user = user_to_update["user"]
    update_user_class.myPass = user_to_update["myPass"]
    update_user_class.billing = json.dumps(user_to_update["billing"])
    update_user_class.shipping = json.dumps(user_to_update["shipping"])
    update_user_class.orderId = json.dumps(user_to_update["orderId"])
    update_user_class.shipping_same_as_billing = user_to_update["shipping_same_as_billing"]

    db.session.flush()
    db.session.commit()
    return {
        'message':{
            'target':user_to_update
        },

    },200



@app.route('/users/delete',methods=['DELETE'])
def delete_user():
    # user needs password before they can delete
    return {
        'message':{'message':"NEED CREDENTIALS"}
    },304
    data = request.json['data']
    user = User.query.filter_by(user=data['user']).first()
    if user is None:
        return {
            'message':{'message':'NOT FOUND'}
        },404
    db.session.delete(user)
    db.session.commit()
    return {
        'message':{'message':'DELETED'},
    },200

@app.route('/users/adminDelete',methods=['DELETE'])
def admin_delete_user():
    # important make sure this is protected
    data = request.json['data']
    user = User.query.filter_by(user=data['user']).first()
    if user is None:
        return {
            'message':{'message':'NOT FOUND'}
        },404
    db.session.delete(user)
    db.session.commit()
    return {
        'message':{'message':'DELETED'},
    },200


@app.route('/users/list',methods=['POST'])
def list_users():
    # if admin requests then supply, you dont want this on the backend
    data = request.json.get('data',{})
    my_filter = data.get('filter') or ['myPass']
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
    items = users_schema.jsonify(User.query.slice(start, stop).all()).json


    # filter according to the query
    if my_filter is not None:
        for x in items:
            for y in my_filter:
                del x[y]
    #
    items = [ {
        **x,
        **{ y:json.loads(x[y]) if x[y] is not None else None for y in ['orderId','billing','shipping']},

    } for x in items]


    return{
        'message':{
            'list':items
        }
    }, 200
