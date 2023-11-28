from .ai_filters import AIFiltersDocker
from krita import DockWidgetFactory, DockWidgetFactoryBase

from .ai_filters import AIFiltersDocker

dock_widget_factory = DockWidgetFactory('ai_filters', DockWidgetFactoryBase.DockRight, AIFiltersDocker)
Krita.instance().addDockWidgetFactory(dock_widget_factory)

