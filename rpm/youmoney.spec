Name: YouMoney
Version: 0.6.6
Release: 1
Summary: YouMoney - free personal finance software
Group: Applications/Archiving
License: GPL
Vendor: zhaoweikid <zhaoweikid@gmail.com>
URL: http://code.google.com/p/youmoney/
Source: %{name}-%{version}.zip
Requires: python >= 2.5 
Requires: wxPython >= 2.8.9.0

%description
YouMoney is a simple personal finance software for you. Support Windows, Linux, MacOS X.

%prep
%setup -q

%build

%install
mkdir -p $RPM_BUILD_ROOT%{_prefix}/bin
mkdir -p $RPM_BUILD_ROOT%{_prefix}/share/YouMoney
mkdir -p $RPM_BUILD_ROOT%{_prefix}/share/YouMoney/ui
mkdir -p $RPM_BUILD_ROOT%{_prefix}/share/YouMoney/data
mkdir -p $RPM_BUILD_ROOT%{_prefix}/share/YouMoney/images
mkdir -p $RPM_BUILD_ROOT%{_prefix}/share/YouMoney/lang
mkdir -p $RPM_BUILD_ROOT%{_prefix}/share/applications

#install -m 755 youmoney $RPM_BUILD_ROOT%{_prefix}/bin
rm -rf $RPM_BUILD_ROOT%{_prefix}/bin/youmoney
echo "#!/bin/bash" >> $RPM_BUILD_ROOT%{_prefix}/bin/youmoney
echo "/usr/bin/python %{_prefix}/share/YouMoney/youmoney.py" >> $RPM_BUILD_ROOT%{_prefix}/bin/youmoney

cp data/category.csv $RPM_BUILD_ROOT%{_prefix}/share/YouMoney/data
cp *.py $RPM_BUILD_ROOT%{_prefix}/share/YouMoney/
cp YouMoney.desktop $RPM_BUILD_ROOT%{_prefix}/share/YouMoney/
cp YouMoney.desktop $RPM_BUILD_ROOT%{_prefix}/share/applications/
cp ui/*.py $RPM_BUILD_ROOT%{_prefix}/share/YouMoney/ui/
cp -R lang $RPM_BUILD_ROOT%{_prefix}/share/YouMoney/
cp -R images $RPM_BUILD_ROOT%{_prefix}/share/YouMoney/

%clean
rm -rf $RPM_BUILD_ROOT

%post
chmod 755 $RPM_BUILD_ROOT%{_prefix}/bin/youmoney

%preun
rm -rf /usr/share/YouMoney
rm -rf /usr/share/applications/YouMoney.desktop

%files
%defattr(-,root,root)
%{_prefix}/bin/youmoney
%{_prefix}/share/applications/YouMoney.desktop
%{_prefix}/share/YouMoney/YouMoney.desktop
%{_prefix}/share/YouMoney/lang/en_US/LC_MESSAGES/*
%{_prefix}/share/YouMoney/lang/zh_CN/LC_MESSAGES/*
%{_prefix}/share/YouMoney/lang/ja_JP/LC_MESSAGES/*
%{_prefix}/share/YouMoney/images/*
%{_prefix}/share/YouMoney/data/*
%{_prefix}/share/YouMoney/*.py
%{_prefix}/share/YouMoney/*.pyc
%{_prefix}/share/YouMoney/*.pyo
%{_prefix}/share/YouMoney/ui/*.py
%{_prefix}/share/YouMoney/ui/*.pyc
%{_prefix}/share/YouMoney/ui/*.pyo
