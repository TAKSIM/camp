# -*- coding: utf-8 -*-
from PyQt4 import QtGui, QtSql
import datetime
from panel_base import PanelBase


class NewSubscription(PanelBase):
    def __init__(self, parent=None, viewOnly=False, **kwargs):
        PanelBase.__init__(self, parent, viewOnly, **kwargs)
        self.standardtenors = ['14', '30', '60', '90', '120', '150', '180', '210', '240', '270', '300', '330', '360', '720']
        self.setWindowTitle(u'添加认购信息')
        self.setWindowIcon(QtGui.QIcon('icons/tent.png'))
        td = datetime.date.today()
        layout = QtGui.QGridLayout()
        layout.addWidget(QtGui.QLabel(u'客户类型'), 0, 0, 1, 1)
        q = QtSql.QSqlQuery('SELECT TYPE_NAME FROM CLIENT_TYPE')
        names = []
        while q.next():
            names.append(q.value(0).toString())
        self.clientType = QtGui.QComboBox()
        if names:
            self.clientType.addItems(names)
        layout.addWidget(self.clientType, 0, 1, 1, 1)
        layout.addWidget(QtGui.QLabel(u'委托人名称'), 1, 0, 1, 1)
        self.clientname = QtGui.QComboBox()
        clientnames=[]
        q = QtSql.QSqlQuery('SELECT DISTINCT CLIENT_NAME FROM LIABILITY')
        while q.next():
            clientnames.append(q.value(0).toString())
        if clientnames:
            self.clientname.addItems(clientnames)
        self.clientname.setEditable(True)
        layout.addWidget(self.clientname, 1, 1, 1, 1)
        layout.addWidget(QtGui.QLabel(u'销售类型：'),2,0,1,1)
        self.salebtn = QtGui.QButtonGroup()
        self.rbDirect = QtGui.QRadioButton(u'直销(A)')
        self.rbIndirect = QtGui.QRadioButton(u'代销(B)')
        self.salebtn.addButton(self.rbDirect)
        self.salebtn.addButton(self.rbIndirect)
        self.rbDirect.setChecked(True)
        self.gbsaletype = QtGui.QGroupBox()
        layout_gbsaletype = QtGui.QHBoxLayout()
        layout_gbsaletype.addWidget(self.rbDirect)
        layout_gbsaletype.addWidget(self.rbIndirect)
        self.gbsaletype.setLayout(layout_gbsaletype)
        layout.addWidget(self.gbsaletype, 2, 1, 1, 1)
        layout.addWidget(QtGui.QLabel(u'认购金额(元)'),3,0,1,1)
        self.amount = QtGui.QLineEdit()
        self.amount.setValidator(QtGui.QDoubleValidator(0., 10000000000., 2))
        self.amount.textChanged.connect(self.calc_totalrtn)
        layout.addWidget(self.amount, 3, 1, 1, 1)
        layout.addWidget(QtGui.QLabel(u'预期收益率(%)'), 4, 0, 1, 1)
        self.rtn = QtGui.QLineEdit()
        self.rtn.setValidator(QtGui.QDoubleValidator(0., 100., 2))
        self.rtn.textChanged.connect(self.calc_totalrtn)
        layout.addWidget(self.rtn, 4, 1, 1, 1)
        layout.addWidget(QtGui.QLabel(u'认购日'), 5, 0, 1, 1)
        self.subdate = QtGui.QDateEdit(td)
        self.subdate.setCalendarPopup(True)
        self.subdate.dateChanged.connect(self.datecheck)
        layout.addWidget(self.subdate, 5, 1, 1, 1)
        layout.addWidget(QtGui.QLabel(u'封闭期起始日'), 6, 0, 1, 1)
        self.settledate = QtGui.QDateEdit(td)
        self.settledate.setCalendarPopup(True)
        self.settledate.dateChanged.connect(self.datecheck)
        layout.addWidget(self.settledate, 6, 1, 1, 1)
        self.gbtenor = QtGui.QGroupBox(u'认购期限')
        self.tenorbtn = QtGui.QButtonGroup()
        self.rbX = QtGui.QRadioButton(u'标准期限(X型)')
        self.rbY = QtGui.QRadioButton(u'订制期限(Y型)')
        self.rbH = QtGui.QRadioButton(u'活期(H型)')
        self.tenorbtn.addButton(self.rbX)
        self.tenorbtn.addButton(self.rbY)
        self.tenorbtn.addButton(self.rbH)
        self.tenorbtn.buttonClicked.connect(self.tenorbtn_clicked)
        self.rbX.setChecked(True)
        layout_tenor = QtGui.QGridLayout()
        layout_tenor.addWidget(self.rbX, 0, 0, 1, 1)
        layout_tenor.addWidget(self.rbY, 1, 0, 1, 1)
        layout_tenor.addWidget(self.rbH, 2, 0, 1, 1)
        self.xtenors = QtGui.QComboBox()
        self.xtenors.addItems(self.standardtenors)
        self.xtenors.currentIndexChanged.connect(self.tenor_update)
        layout_tenor.addWidget(self.xtenors, 0, 1, 1, 1)
        layout_tenor.addWidget(QtGui.QLabel(u'天'), 0, 2, 1, 1)
        self.ytenors = QtGui.QLineEdit()
        self.ytenors.setEnabled(False)
        self.ytenors.setValidator(QtGui.QIntValidator())
        self.ytenors.textChanged.connect(self.tenor_update)
        layout_tenor.addWidget(self.ytenors, 1, 1, 1, 1)
        layout_tenor.addWidget(QtGui.QLabel(u'天'), 1, 2, 1, 1)
        self.gbtenor.setLayout(layout_tenor)
        layout.addWidget(self.gbtenor, 7, 0, 1, 2)
        layout.addWidget(QtGui.QLabel(u'封闭期到期日'), 8, 0, 1, 1)
        self.expdate = QtGui.QDateEdit(td + datetime.timedelta(days=13))
        self.expdate.setCalendarPopup(True)
        self.expdate.dateChanged.connect(self.datecheck)
        layout.addWidget(self.expdate, 8, 1, 1, 1)
        layout.addWidget(QtGui.QLabel(u'到期操作'), 9, 0, 1, 1)
        self.expops = QtGui.QComboBox()
        q = QtSql.QSqlQuery('SELECT OPS_NAME FROM EXPOPS_TYPE')
        opstypes = []
        while q.next():
            opstypes.append(q.value(0).toString())
        if opstypes:
            self.expops.addItems(opstypes)
            self.expops.setCurrentIndex(2)
        layout.addWidget(self.expops, 9, 1, 1, 1)
        layout.addWidget(QtGui.QLabel(u'申请书编号'), 10, 0, 1, 1)
        self.subcode = QtGui.QLineEdit()
        self.subcode.textChanged.connect(self.check_subcode)
        layout.addWidget(self.subcode, 10, 1, 1, 1)
        layout.addWidget(QtGui.QLabel(u'到期本息'), 11, 0, 1, 1)
        self.totalrtn = QtGui.QLineEdit()
        self.totalrtn.setEnabled(False)
        layout.addWidget(self.totalrtn, 11, 1, 1, 1)
        layout.addWidget(QtGui.QLabel(u'备注'), 12, 0, 1, 1)
        self.comment = QtGui.QLineEdit()
        layout.addWidget(self.comment, 12, 1, 1, 1)

        layout_okcancel = QtGui.QHBoxLayout()
        layout_okcancel.addWidget(self.cancel)
        layout_okcancel.addWidget(self.ok)
        layout.addLayout(layout_okcancel, 13, 0, 1, 2)

        self.setLayout(layout)

    def calc_totalrtn(self):
        amt, s = self.amount.text().toDouble()
        if s:
            rtn, s = self.rtn.text().toDouble()
            if s:
                t0 = self.settledate.date().toPyDate()
                t1 = self.expdate.date().toPyDate()
                ds = (t1-t0).days+1
                self.totalrtn.setText('{:,.2f}'.format(amt*(1+rtn*ds/36500.)))

    def tenorbtn_clicked(self, *args, **kwargs):
        if self.rbX.isChecked():
            self.ytenors.setEnabled(False)
            self.xtenors.setEnabled(True)
        elif self.rbY.isChecked():
            self.ytenors.setEnabled(True)
            self.xtenors.setEnabled(False)
        else:
            self.ytenors.setEnabled(False)
            self.xtenors.setEditable(False)

    def tenor_update(self, *args, **kwargs):
        if self.rbX.isChecked():
            ds = self.xtenors.currentText().toInt()[0]
        elif self.rbY.isChecked():
            dstr = self.ytenors.text()
            if dstr.isEmpty():
                return
            ds = dstr.toInt()[0]
        else:
            ds = 1
        self.expdate.setDate(self.settledate.date().toPyDate()+datetime.timedelta(days=ds-1))

    def datecheck(self, *args, **kwargs):
        sub = self.subdate.date().toPyDate()
        settle = self.settledate.date().toPyDate()
        exp = self.expdate.date().toPyDate()
        if settle < sub:
            self.settledate.setDate(sub)
            settle = sub
            QtGui.QMessageBox.warning(self, u'错误', u'<b>封闭期起始日</b>不得早于<b>认购日</b>')
        if exp < settle:
            self.expdate.setDate(settle)
            exp = settle
            QtGui.QMessageBox.warning(self, u'错误', u'<b>封闭期到期日</b>不得早于<b>起始日</b>')
        ds = (exp - settle).days + 1
        if str(ds) in self.standardtenors:
            self.rbX.setChecked(True)
            self.tenorbtn_clicked()
            self.xtenors.setCurrentIndex(self.standardtenors.index(str(ds)))
        else:
            self.rbY.setChecked(True)
            self.tenorbtn_clicked()
            self.ytenors.setText(str(ds))
        self.calc_totalrtn()

    def check_validity(self, raiseWarning=False):
        # logic check for all input that could not ensure validity by UI
        if not self.check_subcode():
            if raiseWarning: QtGui.QMessageBox.warning(self, u'错误', u'<b>申请书编号</b>错误')
            return False
        else:
            _, s = self.amount.text().toDouble()
            if not s:
                if raiseWarning: QtGui.QMessageBox.warning(self, u'错误', u'无法辨识<b>认购金额</b>')
                return False
            _, s = self.rtn.text().toDouble()
            if not s:
                if raiseWarning: QtGui.QMessageBox.warning(self, u'错误', u'无法辨识<b>预期收益率</b>')
                return False
        return True

    def check_subcode(self, *args, **kwargs):
        code = self.subcode.text()
        s = True
        if code.isEmpty():
            self.subcode.setToolTip(u'<b>申请书编码</b>不能为空')
            s = False
        else:
            q = QtSql.QSqlQuery("""SELECT SUB_CODE FROM LIABILITY WHERE SUB_CODE='%s'""" % (code))
            while q.next():  # raise warning if code already exists. should not show more than once
                self.subcode.setToolTip(u'该编码已经被使用')
                s = False
        self.check_updateWidgetStatus(self.subcode, s)
        if s: self.subcode.setToolTip(u'该编码可以使用')
        return s

    def toDB(self):
        code = self.subcode.text()
        client_type = self.clientType.currentIndex()
        client_name = self.clientname.currentText()
        sale_type = self.rbDirect.isChecked() and 'A' or 'B'
        amount, _ = self.amount.text().toDouble()
        rtn, _ = self.rtn.text().toDouble()
        subdate = self.subdate.date().toPyDate()
        settledate = self.settledate.date().toPyDate()
        expdate = self.expdate.date().toPyDate()
        expops = self.expops.currentIndex() + 1
        comment = self.comment.text()
        q = QtSql.QSqlQuery()
        try:
            q.exec_("""INSERT INTO LIABILITY VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')""" % (
                code, client_type, client_name, sale_type, amount, rtn, subdate, settledate, expdate, expops, comment))
            QtSql.QSqlDatabase().commit()
        except Exception, e:
            print e.message
            QtSql.QSqlDatabase().rollback()

