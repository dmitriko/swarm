from tornado import escape

from swarm.stuff import Node, VmConfig, HostNic
from swarm.entity import Entity


def get_entity_view(entity):
    if isinstance(entity, VmConfig):
        return VmConfigView(entity)
    if isinstance(entity, Node):
        return NodeHtmlView(entity)
    if isinstance(entity, HostNic):
        return HostNicHtmlView(entity)
    return HtmlView(entity)


def get_link(entity):
    if hasattr(entity, 'title'):
        title = entity.title
    elif hasattr(entity, 'name'):
        title = entity.name
    elif hasattr(entity, 'hostname'):
        title = entity.hostname
    else:
        title = entity.oid

    return "<a href='%s'> %s </a>" % (entity.oid, title)


def table_view(items):
    result = ['<table>']
    for field, value in items:
        result.append('<tr>')
        result.append('<td>%s</td>' % field)
        result.append('<td>%s</td>' % value)
        result.append('</tr>')
    result.append('</table>')
    return '\n'.join(result)


class HtmlView(object):

    BASE_FIELDS = ['oid', 'class', 'created', 'updated']

    def __init__(self, entity):
        self.entity = entity
    
    def get_value(self, field_name):
        if field_name == 'class':
            return self.entity.__class__.__name__
        value = getattr(self.entity, field_name)
        if isinstance(value, Entity):
            return get_link(value)
        return value
        
    def get_fields(self):
        result = []
        for field_name in self.entity._fields.keys():
            if field_name not in self.BASE_FIELDS:
                result.append(field_name)
        return self.BASE_FIELDS + result

    def get_items(self):
        result = []
        for field_name in self.get_fields():
            value = self.get_value(field_name)
            result.append((field_name, value))
        return result

    def get_html(self):
        return table_view(self.get_items())


def get_nic_link(node, name):
    nic = node.get_host_nic(name)
    if nic is None:
        return name
    return "<a href='/%s'> %s </a>" % (nic.oid, name)


class HostNicHtmlView(HtmlView):
    
    def get_fields(self):
        return HtmlView.BASE_FIELDS + [
            'name', 'host', 'mac', 'rx_bytes', 'tx_bytes',
            'inet_addr', 'mask', 'in_bridge', 'bridge_for']

    def get_value(self, field):
        value = HtmlView.get_value(self, field)
        if field == 'bridge_for' and value:
            value = ", ".join([
                    get_nic_link(self.entity.host, x) for x in value])
        if field == 'in_bridge' and value:
            value = get_nic_link(self.entity.host, value)
        return value
        

def simple_link(oid):
    return "<a href='/%s'> %s </a>" % (oid, oid)


class NodeHtmlView(HtmlView):

    def get_fields(self):
        return HtmlView.get_fields(self) + ['storages']

    def get_value(self, field):

        def nic_link(name, oid):
            return "<a href='/%s'> %s </a>" % (oid, name)

        value = HtmlView.get_value(self, field)
        if field == 'vm_procs':
            value = ", ".join([simple_link(x) for x in value.values()])
        if field == 'host_nics':
            value = ", ".join([nic_link(x, y) for x, y in value.items()])
        if field == 'storages':
            value = ", ".join([str(dict(path=p.path, avail=p.storage.avail
                                    )) for p in value])
        return value
    

class VmConfigView(HtmlView):

    def get_fields(self):
        return HtmlView.BASE_FIELDS + [
            'name', 'vcpu', 'memory', 'host',
            'features', 'nics', 'libvirt_xml']


    def get_value(self, field):

        value = HtmlView.get_value(self, field)

        if field == 'features' and value:
            return ', '.join(value)
        if field == 'libvirt_xml':
            return escape.xhtml_escape(value)
        if field == 'nics':
            return [x.to_dict() for x in value]

        return value


def vm_list_tbody(vm_list):
    result = ['<tbody>']
    for vm in vm_list:
        result.append("<tr>")
        memory = int(vm.vm_config.memory) / 1024
        result.append("<td>%s</td>" %  get_link(vm.vm_config))
        result.append("<td>%s</td>" %  vm.vm_config.vcpu)
        result.append("<td>%s Mb</td>" % memory)
        result.append("<td>%s</td>" %  get_link(vm.node))
        result.append("<td>%s</td>" % (
                ", ".join([get_nic_link(vm.node, x.target
                                        ) for x in vm.vm_config.nics])))
    result.append('<td></td></tr></tbody>')
    return '\n'.join(result)


def vm_list_view(vm_list):
    return """<div class="span10">
  <table>
    <thead>
      <tr>
	<th>Name</th>
	<th class="right">VCPU</th>
	<th class="right">Memory</th>
	<th class="right">Host</th>
	<th class="right">Nic</th>
	<th class="right">Actions</th>
      </tr>
    </thead>
   %s
  </table>
</div>""" % vm_list_tbody(vm_list)

