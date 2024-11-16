{{ name | escape | underline}}

.. currentmodule:: {{ module }}

.. autoclass:: {{ name }}
   :show-inheritance:
   :members:

   {% block methods %}
   {% if methods %}
   .. rubric:: {{ _('Methods') }}

   .. autosummary::
      :toctree: {{ name }}

   {% for item in methods %}
      {{ item | filter_out_parent_class_members(name, module) }}
   {%- endfor %}

   {% endif %}
   {% endblock %}


   {% block attributes %}
   {% if attributes %}
   .. rubric:: {{ _('Attributes') }}

   .. autosummary::
      :nosignatures:
      :toctree: {{ name }}

   {% for item in attributes %}
      {{ item | filter_out_parent_class_members(name, module) }}
   {%- endfor %}

   {% endif %}
   {% endblock %}
