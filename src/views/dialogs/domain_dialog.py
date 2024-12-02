from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                            QLabel, QLineEdit, QMessageBox, QListWidget,
                            QListWidgetItem, QWidget, QMenu)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

class DomainDialog(QDialog):
    domain_changed = pyqtSignal()  # 当域名变化时发出信号
    
    def __init__(self, domain_model, parent=None):
        super().__init__(parent)
        self.domain_model = domain_model
        self.setWindowTitle("Domain Manager")
        self.setMinimumWidth(500)
        self.resize(800, 570)  # 设置初始大小为 800x570
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 创建字体
        button_font = QFont("Segoe UI", 10)
        
        # 添加新域名区域
        add_layout = QHBoxLayout()
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Name (e.g. Production)")
        self.name_input.setFont(button_font)
        self.name_input.setMinimumHeight(32)
        self.name_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #dcdde1;
                border-radius: 4px;
                padding: 4px 8px;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
            }
        """)
        
        self.domain_input = QLineEdit()
        self.domain_input.setPlaceholderText("Domain (e.g. https://api.example.com)")
        self.domain_input.setFont(button_font)
        self.domain_input.setMinimumHeight(32)
        self.domain_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #dcdde1;
                border-radius: 4px;
                padding: 4px 8px;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
            }
        """)
        
        add_button = QPushButton("Add Domain")
        add_button.setFont(button_font)
        add_button.setMinimumHeight(32)
        add_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #219a52;
            }
        """)
        add_button.clicked.connect(self.add_domain)
        
        add_layout.addWidget(self.name_input)
        add_layout.addWidget(self.domain_input)
        add_layout.addWidget(add_button)
        
        # 域名列表
        self.list_widget = QListWidget()
        self.list_widget.setFont(button_font)
        self.list_widget.setStyleSheet("""
            QListWidget {
                border: 1px solid #dcdde1;
                border-radius: 4px;
                padding: 2px;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 4px;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #f1f2f6;
            }
        """)
        self.list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self.show_context_menu)
        
        # 添加到主布局
        layout.addLayout(add_layout)
        layout.addWidget(self.list_widget)
        
        # 刷新列表
        self.refresh_domains()
        
    def add_domain(self):
        name = self.name_input.text().strip()
        domain = self.domain_input.text().strip()
        
        if not name or not domain:
            QMessageBox.warning(self, "Warning", "Please enter both name and domain")
            return
            
        self.domain_model.add_domain(name, domain)
        self.name_input.clear()
        self.domain_input.clear()
        self.refresh_domains()
        
    def refresh_domains(self):
        self.list_widget.clear()
        domains = self.domain_model.get_all_domains()
        
        for domain in domains:
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, domain)
            
            # 创建自定义widget来显示域名信息
            widget = QWidget()
            layout = QHBoxLayout()
            widget.setLayout(layout)
            
            # 域名信息
            info_layout = QVBoxLayout()
            name_label = QLabel(domain['name'])
            name_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            domain_label = QLabel(domain['domain'])
            domain_label.setFont(QFont("Segoe UI", 9))
            
            info_layout.addWidget(name_label)
            info_layout.addWidget(domain_label)
            
            # 活动状态标签
            if domain['is_active']:
                active_label = QLabel("Active")
                active_label.setStyleSheet("""
                    QLabel {
                        color: #27ae60;
                        font-weight: bold;
                    }
                """)
                layout.addWidget(active_label)
            
            layout.addLayout(info_layout)
            layout.addStretch()
            
            # 设置item的大小
            item.setSizeHint(widget.sizeHint())
            
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, widget)
            
    def show_context_menu(self, pos):
        item = self.list_widget.itemAt(pos)
        if not item:
            return
            
        domain_data = item.data(Qt.ItemDataRole.UserRole)
        
        menu = QMenu()
        menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #dcdde1;
                padding: 5px;
            }
            QMenu::item {
                padding: 5px 20px;
            }
            QMenu::item:selected {
                background-color: #f1f2f6;
            }
        """)
        
        # 如果不是活动域名，显示"设为活动"选项
        if not domain_data['is_active']:
            activate_action = menu.addAction("Set as Active")
            activate_action.triggered.connect(lambda: self.set_active_domain(domain_data['id']))
            
        edit_action = menu.addAction("Edit")
        edit_action.triggered.connect(lambda: self.edit_domain(domain_data))
        
        delete_action = menu.addAction("Delete")
        delete_action.triggered.connect(lambda: self.delete_domain(domain_data['id']))
        
        menu.exec(self.list_widget.mapToGlobal(pos))
        
    def set_active_domain(self, id):
        self.domain_model.set_active_domain(id)
        self.refresh_domains()
        self.domain_changed.emit()
        
    def edit_domain(self, domain_data):
        dialog = EditDomainDialog(domain_data, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name = dialog.name_input.text().strip()
            domain = dialog.domain_input.text().strip()
            self.domain_model.update_domain(domain_data['id'], name, domain)
            self.refresh_domains()
            self.domain_changed.emit()
            
    def delete_domain(self, id):
        reply = QMessageBox.question(
            self, 'Confirm Delete',
            'Are you sure you want to delete this domain?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.domain_model.delete_domain(id)
            self.refresh_domains()
            self.domain_changed.emit()
            
class EditDomainDialog(QDialog):
    def __init__(self, domain_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Domain")
        self.domain_data = domain_data
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 输入框
        self.name_input = QLineEdit(self.domain_data['name'])
        self.domain_input = QLineEdit(self.domain_data['domain'])
        
        layout.addWidget(QLabel("Name:"))
        layout.addWidget(self.name_input)
        layout.addWidget(QLabel("Domain:"))
        layout.addWidget(self.domain_input)
        
        # 按钮
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        cancel_button = QPushButton("Cancel")
        
        save_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
