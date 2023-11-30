from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QStackedWidget,
    QComboBox,
    QToolButton,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
)
from PyQt5.QtCore import Qt, QSize
from krita import DockWidget

from .vtoonify import VToonify
from .dualstylegan import DualStyleGAN
from .esrgan import ESRGAN
from .semantic_segmentation import SemanticSegmentation
from .deblur import Deblur
from .rembg import RemBg

STR_APPLY = "Apply Filter"
STR_CANCEL = "Cancel"

class MessageLine(QLabel):

    def __init__(self, str=None):
        self._cachedText = ""
        self._cachedElidedText = ""

        super().__init__(str)
        self.setAlignment(Qt.AlignLeft|Qt.AlignTop)

        self.setMultiline(False)

    def setText(self, text):
        super().setText(text)
        self.repaint()
        QApplication.processEvents()

    def setMultiline(self, multiline):
        self.multiline = multiline
        self.setWordWrap(self.multiline)
        self.updateCachedTexts(True)

    def updateCachedTexts(self, force=False):
        txt = self.text()
        if (not force and self._cachedText == txt):
            return
        self._cachedText = txt
        fm = self.fontMetrics()
        self._cachedElidedText = fm.elidedText(
             self._cachedText, not self.multiline,
             self.width(), Qt.TextShowMnemonic
        )
        if (self._cachedText):
             showFirstCharacter = self._cachedText[0] + "..."
             self.setMinimumWidth(fm.horizontalAdvance(showFirstCharacter) + 1)
        if self.multiline:
             self.setMinimumHeight(fm.height())
             self.setMaximumHeight(16777215)
        else:
             self.setMinimumHeight(fm.height())
             self.setMaximumHeight(fm.height())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.updateCachedTexts(True)

    def paintEvent(self, event):
        self.updateCachedTexts()
        if self.multiline:
            super().paintEvent(event)
        else:
            super().setText(self._cachedElidedText)
            super().paintEvent(event)
            super().setText(self._cachedText)

    def mousePressEvent(self, event):
        self.setMultiline(not self.multiline)

class AIFiltersDocker(DockWidget):

    def __init__(self):

        super().__init__()
        self.setWindowTitle('AI Filters')

        self.filters = [RemBg(self), VToonify(self), DualStyleGAN(self), ESRGAN(self), SemanticSegmentation(self), Deblur(self)]

        frame = QWidget(self)
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(0, 0, 0, 0)
        frame.setLayout(frame_layout)

        filter_select_row = QWidget(self)
        filter_select_row_layout = QHBoxLayout(filter_select_row)
        filter_select_row_layout.setContentsMargins(0, 0, 0, 0)
        filter_select_row.setLayout(filter_select_row_layout)

        # more information
        info = QToolButton(filter_select_row)
        info.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        info.autoRaise()
        info.setText("...")
        info.clicked.connect(self.show_info)

        # filter selections   
        self.filter_select = QComboBox(filter_select_row)
        self.filter_select.setStyleSheet(
            "QComboBox { border:none; background-color:transparent; padding: 1px 12px 1px 2px;}"
        )
        self.filter_select.currentIndexChanged.connect(self.filterChanged)

        # message
        self.message = MessageLine()

        # filter options
        self.filter_options = QStackedWidget(self)

        # populate filters
        for filter in self.filters:
            self.filter_select.addItem(filter.title, filter.name)
            self.filter_options.addWidget(filter) 
        
        filter_select_row_layout.addWidget(self.filter_select)
        filter_select_row_layout.addWidget(info)

        frame_layout.addWidget(filter_select_row)
        frame_layout.addWidget(self.message)
        frame_layout.addWidget(self.filter_options)

        self.applyButton = QPushButton(STR_APPLY, self)
        self.applyButton.clicked.connect(self.apply)
        frame_layout.addWidget(self.applyButton)
        
        self.setWidget(frame)
        self.checkEnabled()

        self.components = [filter_select_row, self.filter_options, self.applyButton]

    def checkEnabled(self):
        index = self.filter_select.currentIndex()
        filter = self.filter_options.widget(index)
        if filter:
            enabled = filter.enabled()
            self.applyButton.setEnabled(enabled)
       
    def filterChanged(self):
        index = self.filter_select.currentIndex()
        self.filter_options.setCurrentIndex(index)
        self.checkEnabled()

    def show_info(self):
        from PyQt5.QtGui import QDesktopServices
        from PyQt5.QtCore import QUrl
        index = self.filter_select.currentIndex()
        filter = self.filter_options.widget(index)
        QDesktopServices.openUrl(QUrl(filter.info))

    def updateMessage(self, message):
        self.message.setText(message)

    def apply(self):
        index = self.filter_select.currentIndex()
        if self.applyButton.text() == STR_CANCEL:
            self.filter_options.widget(index).kill()
        else:
            for component in self.components:
                component.setEnabled(False)
            index = self.filter_select.currentIndex()
            self.applyButton.setText(STR_CANCEL)
            self.applyButton.setEnabled(True)
            self.filter_options.widget(index).run_outer(self.updateMessage)
            self.updateMessage("")
            self.applyButton.setText(STR_APPLY)
            for component in self.components:
                component.setEnabled(True)
            self.checkEnabled()

    def canvasChanged(self, canvas):
        self.checkEnabled()
