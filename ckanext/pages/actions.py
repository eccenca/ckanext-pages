import datetime

import ckan.plugins as p
import ckan.lib.navl.dictization_functions as df
import ckan.new_authz as new_authz
import logging
import pylons


import db
logger = logging.getLogger(__name__)

LANGS = ['en', 'fr', 'de', 'es', 'it', 'nl', 'ro', 'pt', 'pl']

def page_name_validator(key, data, errors, context):
    session = context['session']
    page = context.get('page')
    group_id = context.get('group_id')
    if page and page == data[key]:
        return

    query = session.query(db.Page.name).filter_by(name=data[key], group_id=group_id, lang=context.get('lang'))
    result = query.first()
    if result:
        errors[key].append(
            p.toolkit._('Page name already exists in database'))

schema = {
    'id': [p.toolkit.get_validator('ignore_empty'), unicode],
    'title': [p.toolkit.get_validator('not_empty'), unicode],
    'name': [p.toolkit.get_validator('not_empty'), unicode,
             p.toolkit.get_validator('name_validator'), page_name_validator],
    'content': [p.toolkit.get_validator('ignore_missing'), unicode],
    'lang': [p.toolkit.get_validator('not_empty'), unicode],
    'order': [p.toolkit.get_validator('ignore_missing'),
              unicode],
    'private': [p.toolkit.get_validator('ignore_missing'),
                p.toolkit.get_validator('boolean_validator')],
    'group_id': [p.toolkit.get_validator('ignore_missing'), unicode],
    'user_id': [p.toolkit.get_validator('ignore_missing'), unicode],
    'created': [p.toolkit.get_validator('ignore_missing'),
                p.toolkit.get_validator('isodate')],
}


def _pages_show(context, data_dict):
    lang = get_language()
    if db.pages_table is None:
        db.init_db(context['model'])
    org_id = data_dict.get('org_id')
    page = data_dict.get('page')
    out = db.Page.get(group_id=org_id, name=page, lang=lang) 
    # , lang= get_language()
    if out:
        out = db.table_dictize(out, context)
    return out


def _pages_list(context, data_dict):
    #lang = get_language()
    search = {}
    #search['lang'] = lang
    if db.pages_table is None:
        db.init_db(context['model'])
    org_id = data_dict.get('org_id')
    ordered = data_dict.get('order')
    private = data_dict.get('private', True)
    if ordered:
        search['order'] = True
    if not org_id:
        search['group_id'] = None
        try:
            p.toolkit.check_access('ckanext_pages_update', context, data_dict)
            if not private:
                search['private'] = False
        except p.toolkit.NotAuthorized:
            search['private'] = False
    else:
        group = context['model'].Group.get(org_id)
        user = context['user']
        member = new_authz.has_user_permission_for_group_or_org(
            group.id, user, 'read')
        search['group_id'] = org_id
        if not member:
            search['private'] = False
    out = db.Page.pages(**search)
    return [{'title': pg.title,
             'content': pg.content,
             'name': pg.name,
             'lang': pg.lang,
             'group_id': pg.group_id,
            } for pg in out]


def _pages_delete(context, data_dict):
    lang = get_language()
    if db.pages_table is None:
        db.init_db(context['model'])
    org_id = data_dict.get('org_id')
    page = data_dict.get('page')
    out = db.Page.get(group_id=org_id, name=page, lang=lang)
    if out:
        session = context['session']
        session.delete(out)
        session.commit()


def _pages_update(context, data_dict):
    lang = get_language()
    if db.pages_table is None:
        db.init_db(context['model'])
    org_id = data_dict.get('org_id')
    page = data_dict.get('page')
    # we need the page in the context for name validation
    context['page'] = page
    context['group_id'] = org_id

    data, errors = df.validate(data_dict, schema, context)

    if errors:
        raise p.toolkit.ValidationError(errors)

    out = db.Page.get(group_id=org_id, name=page, lang=lang)
    if not out:
        out = db.Page()
        out.group_id = org_id
        out.name = page
        out.lang = lang
    items = ['title', 'content', 'name', 'lang', 'private', 'order']

    for item in items:
        setattr(out, item, data.get(item))

    out.modified = datetime.datetime.utcnow()
    out.user_id = p.toolkit.c.userobj.id
    out.save()
    session = context['session']
    session.add(out)
    session.commit()


def pages_show(context, data_dict):
    try:
        p.toolkit.check_access('ckanext_pages_show', context, data_dict)
    except p.toolkit.NotAuthorized:
        p.toolkit.abort(401, p.toolkit._('Not authorized to see this page'))
    return _pages_show(context, data_dict)


def pages_update(context, data_dict):
    try:
        p.toolkit.check_access('ckanext_pages_update', context, data_dict)
    except p.toolkit.NotAuthorized:
        p.toolkit.abort(401, p.toolkit._('Not authorized to see this page'))
    return _pages_update(context, data_dict)


def pages_delete(context, data_dict):
    try:
        p.toolkit.check_access('ckanext_pages_delete', context, data_dict)
    except p.toolkit.NotAuthorized:
        p.toolkit.abort(401, p.toolkit._('Not authorized to see this page'))
    return _pages_delete(context, data_dict)


def pages_list(context, data_dict):
    try:
        p.toolkit.check_access('ckanext_pages_list', context, data_dict)
    except p.toolkit.NotAuthorized:
        p.toolkit.abort(401, p.toolkit._('Not authorized to see this page'))
    return _pages_list(context, data_dict)


def org_pages_show(context, data_dict):
    try:
        p.toolkit.check_access('ckanext_org_pages_show', context, data_dict)
    except p.toolkit.NotAuthorized:
        p.toolkit.abort(401, p.toolkit._('Not authorized to see this page'))
    return _pages_show(context, data_dict)


def org_pages_update(context, data_dict):
    try:
        p.toolkit.check_access('ckanext_org_pages_update', context, data_dict)
    except p.toolkit.NotAuthorized:
        p.toolkit.abort(401, p.toolkit._('Not authorized to see this page'))
    return _pages_update(context, data_dict)


def org_pages_delete(context, data_dict):
    try:
        p.toolkit.check_access('ckanext_org_pages_delete', context, data_dict)
    except p.toolkit.NotAuthorized:
        p.toolkit.abort(401, p.toolkit._('Not authorized to see this page'))
    return _pages_delete(context, data_dict)


def org_pages_list(context, data_dict):
    try:
        p.toolkit.check_access('ckanext_org_pages_list', context, data_dict)
    except p.toolkit.NotAuthorized:
        p.toolkit.abort(401, p.toolkit._('Not authorized to see this page'))
    return _pages_list(context, data_dict)


def group_pages_show(context, data_dict):
    try:
        p.toolkit.check_access('ckanext_group_pages_show', context, data_dict)
    except p.toolkit.NotAuthorized:
        p.toolkit.abort(401, p.toolkit._('Not authorized to see this page'))
    return _pages_show(context, data_dict)


def group_pages_update(context, data_dict):
    try:
        p.toolkit.check_access('ckanext_group_pages_update', context, data_dict)
    except p.toolkit.NotAuthorized:
        p.toolkit.abort(401, p.toolkit._('Not authorized to see this page'))
    return _pages_update(context, data_dict)


def group_pages_delete(context, data_dict):
    try:
        p.toolkit.check_access('ckanext_group_pages_delete', context, data_dict)
    except p.toolkit.NotAuthorized:
        p.toolkit.abort(401, p.toolkit._('Not authorized to see this page'))
    return _pages_delete(context, data_dict)


def group_pages_list(context, data_dict):
    try:
        p.toolkit.check_access('ckanext_group_pages_list', context, data_dict)
    except p.toolkit.NotAuthorized:
        p.toolkit.abort(401, p.toolkit._('Not authorized to see this page'))
    return _pages_list(context, data_dict)

def get_language():
    lang_set = set(LANGS)
    current_lang = pylons.request.environ['CKAN_LANG']
    # fallback to default locale if locale not in suported langs
    if not current_lang in lang_set:
        current_lang = config.get('ckan.locale_default')
    # fallback to english if default locale is not supported
    if not current_lang in lang_set:
        current_lang = 'en'
    # treat current lang differenly so remove from set
    lang_set.remove(current_lang)
    return current_lang  
