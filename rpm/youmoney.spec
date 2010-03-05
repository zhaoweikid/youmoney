Name: YouMoney
Version: 0.6.5
Release: 65
Summary: YouMoney - free personal finance software
Group: Applications/Archiving
License: GPL
Vendor: zhaoweikid <zhaoweikid@gmail.com>
URL: http://code.google.com/p/youmoney/
Source0: http://youmoney.googlecode.com/files/${name}-src-${version}.zip
BuildRequires: binutils >= 2.9.1.0.23
PreReq: /sbin/install-info
Requires: python >= 2.5 
Requires: wxPython >= 2.8.9.0

%description
YouMoney is a simple personal finance software for you. Support Windows, Linux, MacOS X.

%prep
%setup -q

%build

%install

%clean
rm -fr $RPM_BUILD_ROOT

%post

%preun

%files
%defattr(-,root,root)
%doc AUTHORS ChangeLog README COPYING TODO
