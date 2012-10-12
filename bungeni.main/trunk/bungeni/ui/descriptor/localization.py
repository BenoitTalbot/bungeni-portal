# Bungeni Parliamentary Information System - http://www.bungeni.org/
# Copyright (C) 2010 - Africa i-Parliaments - http://www.parliaments.info/
# Licensed under GNU GPL v2 - http://www.gnu.org/licenses/gpl-2.0.txt

"""Localization of Form Schema Descriptors

$Id$
"""
log = __import__("logging").getLogger("bungeni.ui.descriptor.localization")

from time import time
import elementtree.ElementTree
from bungeni.alchemist.model import (
    #ModelDescriptor,
    IModelDescriptor,
    Field,
    show, hide,
    #norm_sorted,
)
from bungeni.ui.descriptor import field
from bungeni.utils.capi import capi, bungeni_custom_errors
from bungeni.utils import naming, misc

# constants 

from bungeni.ui.descriptor import descriptor as DESCRIPTOR_MODULE

PATH_UI_FORMS_SYSTEM = capi.get_path_for("forms", "ui.xml")
PATH_UI_FORMS_CUSTOM = capi.get_path_for("forms", "custom.xml")

ROLES_DEFAULT = " ".join(Field._roles)


####
# Load and apply forms localization --
# Localize descriptors from {bungeni_custom}/forms/.

def is_descriptor(cls):
    try:
        return IModelDescriptor.implementedBy(cls)
    except (TypeError, AttributeError):
        return False
    '''
    try:
        return issubclass(cls, ModelDescriptor):
    except TypeError:
        return False
    '''

def get_localizable_descriptor_class(module, type_key):
    """Retrieve an existing localizable descriptor class from module.
    Raise AttributeError if not existing -> descriptor to be created.
    Raise AssertionError if exists but is either not a descriptor cls or 
    is not localizable.
    """
    descriptor_cls_name = naming.descriptor_class_name(type_key)
    cls = getattr(module, descriptor_cls_name) # raises AttributeError
    assert is_descriptor(cls), \
        "Invalid descriptor [%s]" % (descriptor_cls_name)
    assert cls.localizable, \
        "May not localize a non-localizable descriptor [%s]" % (
            descriptor_cls_name)
    return cls

''' !+UNUSED
def reorder_fields(cls, ordered_field_names, field_by_name):
    """Reorder descriptor class fields.
    """
    log.debug("reorder_fields [%s] %s" % (cls.__name__, ordered_field_names))
    # validate
    assert len(cls.fields) == len(ordered_field_names), \
        "Localization of [%s]: Field list does not match:\nB: %s\nC: %s" % (
            cls.__name__, [ f.name for f in cls.fields ], ordered_field_names )
    for f in cls.fields:
        assert f.name in ordered_field_names, \
            "Localization of [%s]: Unspecified order for field [%s]" % (
                cls.__name__, f.name)
        field_by_name[f.name] = f
    # reorder (retaining same list instance as class attribute)
    cls.fields[:] = [ field_by_name[name] for name in ordered_field_names ]

def is_stale_info(bval, cval, message):
    if not bval == cval:
        log.warn(message)
        return True
    return False
'''

def check_reload_localization(event):
    """Called once on IWSGIApplicationCreatedEvent and (if in DEVMODE)
    once_per_request on IBeforeTraverseEvent events (ui.publication).
    """
    for file_path in [PATH_UI_FORMS_SYSTEM, PATH_UI_FORMS_CUSTOM]:
        if capi.is_modified_since(file_path):
            localize_descriptors(file_path)

@bungeni_custom_errors
def localize_descriptors(file_path):
    """Localizes descriptors from {bungeni_custom}/forms/ui.xml.
    """
    start_time = time()
    xml = elementtree.ElementTree.fromstring(misc.read_file(file_path))
    # make the value of <ui.@roles> as *the* bungeni default list of roles
    global ROLES_DEFAULT
    Field._roles[:] = xml.get("roles", ROLES_DEFAULT).split()
    # and reset global "constant" !+DECL ui.@roles must be set only once!
    ROLES_DEFAULT = " ".join(Field._roles)
    
    import bungeni.alchemist
    def reset_zope_schema_properties_on_model_interface(descriptor_cls):
        type_key = naming.type_key("descriptor_class_name", descriptor_cls.__name__)
        ti = capi.get_type_info(type_key)
        domain_model = ti.domain_model
        sast = bungeni.alchemist.catalyst.SQLAlchemySchemaTranslator()
        domain_table = bungeni.alchemist.utils.get_local_table(domain_model)
        # zope.schema field property map
        zsfp_map = sast.generateFields(domain_table, descriptor_cls)
        # apply manually overridden field properties
        sast.applyProperties(zsfp_map, descriptor_cls)
        # stuff back onto derived_table_schema
        derived_table_schema = ti.derived_table_schema
        assert len(derived_table_schema.names(all=False)) == len(zsfp_map)
        for name in derived_table_schema.names(all=False):
            assert name in zsfp_map
            # !+ zsfp == descriptor_cls.fields_by_name[name].property
            zsfp = zsfp_map[name]
            # !+property.__name__ needed downstream by 
            # zope.formlib.form.FormField __init__() does assert name !?!
            zsfp.__name__ = name
            # !+ cannot simply set the property directly on derived_table_schema:
            #   derived_table_schema[f.name] = zsfp
            # as this gives: 
            #   *** TypeError: 'InterfaceClass' object does not support item assignment
            # So we have to workaround it !!
            derived_table_schema._InterfaceClass__attrs[name] = zsfp
        # and we need to notify (only once) that the schema has changed 
        derived_table_schema.changed("localize_descriptors")
    '''!+ reset_zope_schema_properties_on_model_interface
    Initially field.property IS derived_table_schema[f.name], and so if field config
    changes then the derived_table_schema has to be "kept in sync". 
    
    Above does it the "alchemist" way, but it could certainly be a lot simpler 
    and faster, at least for "repeat" syncing with changed fields. Examples:
    
    a) (if we ignore the issue of not being able to directly set property on 
    derived_table_schema) this could simply be done with something like:
    
        for f in cls.fields:
            if f.property is not None:
                derived_table_schema[f.name] = f.property
    
    b) it may (should!) be possible to make this completely dynamic... that is 
    to give the IIModelInterface interfaces the intelligence to always 
    dynamically pull the field.property directly!
    '''
    
    def new_descriptor_cls(type_key, archetype, **kw):
        descriptor_cls_name = naming.descriptor_class_name(type_key)
        attrs = {}
        for key in kw:
            if kw[key] is not None:
                attrs[key] = kw[key]
        attrs.update({
                "scope": "custom", 
                "__module__": DESCRIPTOR_MODULE.__name__
            })
        cls = type(descriptor_cls_name, (archetype,), attrs)
        # set on DESCRIPTOR_MODULE
        setattr(DESCRIPTOR_MODULE, descriptor_cls_name, cls)
        log.info("localize_descriptors [type=%s] generated descriptor %s.%s" % (
                type_key, DESCRIPTOR_MODULE.__name__, descriptor_cls_name))
        return cls
    
    def new_descriptor_fields(edescriptor):
        """(Re-)build (in desired order) all fields from newly loaded 
        descriptor configuration.
        # !+ what about "removed" fields from a sys-descriptor config?
        """
        xas, xab = misc.xml_attr_str, misc.xml_attr_bool
        fields = []
        for f_elem in edescriptor.findall("field"):
            # custom_localizable_directives
            clocs = []
            for cloc_elem in f_elem.getchildren():
                modes = xas(cloc_elem, "modes")
                roles = xas(cloc_elem, "roles") # ROLES_DEFAULT
                if cloc_elem.tag == "show":
                    clocs.append(show(modes=modes, roles=roles))
                elif cloc_elem.tag == "hide":
                    clocs.append(hide(modes=modes, roles=roles))
                else:
                    raise ValueError(
                        "Unknown directive %r in field %r in descriptor %r" % (
                            cloc_elem.tag, xas(f_elem, "name"), type_key))
            fields.append(field.F(
                    name=xas(f_elem, "name"),
                    label=xas(f_elem, "label"),
                    description=xas(f_elem, "description"),
                    required=xab(f_elem, "required"),
                    localizable=clocs,
                    value_type=xas(f_elem, "value_type"),
                    render_type=xas(f_elem, "render_type"),
                    vocabulary=xas(f_elem, "vocabulary")
                ))
        return fields
    
    for edescriptor in xml.findall("descriptor"):
        NEW = False
        type_key = misc.xml_attr_str(edescriptor, "name")
        ti = capi.get_type_info(type_key)
        # !+domain_model is it already set?
        if ti.domain_model is None:
            model_name = naming.model_name(type_key)
            import bungeni.models.domain
            ti.domain_model = getattr(bungeni.models.domain, model_name)
            log.warn("localize_descriptors - setting [%s] domain model [%s]" % (
                type_key, ti.domain_model))
        order = misc.xml_attr_int(edescriptor, "order")
        fields = new_descriptor_fields(edescriptor)
        try:
            cls = get_localizable_descriptor_class(DESCRIPTOR_MODULE, type_key)
            if order is not None:
                cls.order = order
            # replace contents of descriptor cls fields list (retaining list 
            # instance) and validate/update descriptor model
            cls.fields[:] = fields
            cls.sanity_check_fields()
        except AttributeError:
            # new custom descriptor
            NEW = True
            archetype_key = misc.xml_attr_str(edescriptor, "archetype")
            assert archetype_key, \
                "Custom descriptor [%s] does not specify an archetype" % (type_key)
            archetype = get_localizable_descriptor_class(DESCRIPTOR_MODULE, archetype_key)
            assert archetype.scope in ("archetype", "custom"), \
                "Invalid archetype %r for descriptor %r" % (
                    archetype_key, type_key)
            cls = new_descriptor_cls(type_key, archetype, 
                    order=order,
                    fields=fields,
                    default_field_order=[ f.name for f in fields ])
            # register as the ti.descriptor_model
            ti.descriptor_model = cls
        
        # first time around need to catalyse custom descriptors
        if NEW and cls.scope == "custom":
            bungeni.alchemist.catalyst.catalyst(ti)
        # push back on alchemist model interface !+
        reset_zope_schema_properties_on_model_interface(cls)
    
    log.warn("LOCALIZING DESCRIPTORS from FILE: %s\n   ...DONE [in %s secs]" % (
        file_path, time()-start_time))



