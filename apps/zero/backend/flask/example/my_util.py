def local_deps():
    import sys
    if sys.platform == "win32":
        sys.path.append(sys.path[0] + ".\\site-packages\\windows")
    elif sys.platform =="linux":
        sys.path.append(sys.path[0] + "./site-packages/linux")    
local_deps()

def translator(d,new_dict={},func=lambda my_str: my_str):

    for val in d.values():
        try:
           translator(val)
        except AttributeError:
           print(val)


def i18n_translate_vendor(dev_obj):
    import json
    from translatepy import Translator
    lang_codes = dev_obj.get("lang_codes")
    source_file = dev_obj.get("source_file")
    dest_file = dev_obj.get("dest_file")

    i18n_trnaslator = Translator()
    for x in lang_codes:

        with open(source_file,encoding="utf-8") as f:
            lang  = json.load(f)
            def translateMe(string):
                my_result = i18n_trnaslator.translate(
                    string,
                    destination_language=x,
                    source_language="en"
                ).result
                print(my_result)
                return my_result

            my_translate = replace(lang,translateMe)


            with open(dest_file.replace("{}",x)
            ,"w",encoding="utf-8") as g:
                print(json.dumps(my_translate,indent=4) , file=g)
                f.close()
                g.close()

    return {
        'data':{
            'i18n_obj':my_translate
        }
    }



def replace(data, repl):
    if isinstance(data, dict):
        return {k: replace(v, repl) for k, v in data.items()}
    elif isinstance(data, list):
        return [replace(x, repl) for x in data]
    else:
        return repl(data)



# update the source to the data,
    # if a prop is not on data, it wont be added
def update_dict(data, source):
    if source is None:
        return data
    elif isinstance(source, dict):
        return {k: update_dict(v, source.get(k)) for k, v in data.items()}
    elif isinstance(source, list):
        diff = len(source) - len(data)
        if(diff > 0):
            [data.append(x) for i,x in enumerate(source) if i > diff ]
        return [update_dict(x, source[i]) for i,x in enumerate(source)]
    else:
        return source




def update_target(data, source,repl= lambda x,y:  y):
    if isinstance(data, dict):
        for k, v in data.items():
            if k in source:
                data[k] = update_target(v, source[k],repl)
        return data
    # elif isinstance(data, list):
    #     if (len(data) < len(source)):
    #         data = data[:len(source)]
    #     return [update_target(x,source[i], repl) for i,x in enumerate(data)]
    else:
        # just update the list
        return repl(data,source)




# DEV ADDITIONS

# DEV ADDITIONS
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID
import uuid

class GUID(TypeDecorator):
    """Platform-independent GUID type.
    Uses PostgreSQL's UUID type, otherwise uses
    CHAR(32), storing as stringified hex values.
    """
    impl = CHAR

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value).int
            else:
                # hexstring
                return "%.32x" % value.int

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                value = uuid.UUID(value)
            return value
