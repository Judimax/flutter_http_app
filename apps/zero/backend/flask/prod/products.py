from prod_app import app,db,ma,request,pprint,json,my_util,users,sqlalchemy
from users import User
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import text as sa_text
import uuid
from my_util import GUID

class Product(db.Model):
    productId = db.Column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(200), nullable = False)
    img_url = db.Column(db.String(1000))
    price = db.Column(db.Float(decimal_return_scale=2), nullable = False)
    quantity = db.Column(db.Integer, nullable = False)

    desc = db.Column(db.String(3000), nullable = True)


    def __init__(self,title,img_url,price,quantity,desc):
        self.title = title
        self.img_url = img_url
        self.price = price
        self.quantity = quantity
        self.desc = desc


    def  any(self):
        return '<pro'

class ProductSchema(ma.Schema):
    class Meta:
        fields = ('title','img_url','price','quantity','desc')

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

@app.route('/product/create',methods=['PUT'])
def create_product():
    data = request.json['data']
    print("\n");

    print(format(float(data['price']),".2f"))
    print("\n");
    newproduct = Product(
        data['title'],
        data['img_url'],
        float(format(float(data['price']),".2f")),
        data['quantity'],
        data['desc'],
    )
    db.session.add(newproduct)
    db.session.commit()
    return {
        'message':{'message':'CREATED'},

    },201

@app.route('/product/read',methods=['POST'])
def read_product():
    data = request.json['data']
    productID = data['title']
    product = Product.query.filter_by(title= productID).first()
    if product is None:
       return  {
           'message':{'message':'Product not found'},

        }, 404

    else:
       return  {
            'message':{
                'message':'OK',
                'data':product_schema.dump(product)
            },

        },200




@app.route('/product/update',methods=['PATCH'])
def update_product():
    data = request.json['data']
    product = data['title']
    update_body = data["update_body"]
    update_class = Product.query.filter_by(title=product).first()

    if update_class is None:
        return {
            'message':{'message':'Product not found'},
        },404
    target_to_update = product_schema.dump(update_class)
    target_to_update = my_util.update_target(target_to_update,update_body)

    def target_class_update(attr,val,idx):
        setattr(update_class,attr, val)

    [
        target_class_update(x,target_to_update[x],i)
        for i,x in enumerate(["desc","img_url","price","quantity","title"])
    ]

    db.session.flush()
    db.session.commit()
    return {
        'message':{
            'target':target_to_update
        },

    },200


@app.route('/product/delete',methods=['DELETE'])
def delete_product():
    data = request.json['data']
    product = Product.query.filter_by(title=data['title']).first()
    db.session.delete(product)
    db.session.commit()
    return {
        'message':{'message':'DELETED'},
    },200

    None

@app.route('/product/list',methods=['POST'])
def list_products():

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

    items = products_schema.jsonify(Product.query.slice(start, stop).all()).json

    # filter according to the query
    if my_filter is not None:
        for x in items:
            for y in my_filter:
                del x[y]
    #
    #

    items = [ {
        **x,

    } for x in items]

    return{
        'message':{
            'list':items
        }
    }, 200
