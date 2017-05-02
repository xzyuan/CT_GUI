# CT_GUI

## Structure

```
├── GUI.py  # CT core code
├── XPS_Q8_drivers.py  # motor driver
├── __pycache__
│   ├── XPS_Q8_drivers.cpython-35.pyc
│   └── mainwindow.cpython-35.pyc
├── conf.json  # some configuration
├── conf_1.json  
├── conf_2.json
├── conf_3.json
├── main.py  # CLI for CT
├── mainwindow.py  # GUI code from turnning mainwindow.ui by tool of pic
└── mainwindow.ui  # qtDisigner create a ui file
```


## working log

---
2016-04-28：

* motor move page has completed.

* using *.json files configurates scanning parameters.

* 3 *.json files corresponde to 3 modes. 

---
2016-04-27：

* fixed xps_driver to support Python3, more details in xps_driver file where marked "fixed"
