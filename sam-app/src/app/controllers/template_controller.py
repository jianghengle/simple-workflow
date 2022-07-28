from ..models.template_model import TemplateModel

def get_all_templates(req):
    templates = TemplateModel.get_all()
    return [t.data for t in templates]

def get_template(req, id):
    template = TemplateModel.get_by_id(id)
    return template.data

