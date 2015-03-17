%{!?gitrev: %global gitrev 3a22891}
%{!?hawkey_version: %global hawkey_version 0.5.3}
%{!?librepo_version: %global librepo_version 1.7.5}
%{!?libcomps_version: %global libcomps_version 0.1.6}
%{!?rpm_version: %global rpm_version 4.12.0}

%global confdir %{_sysconfdir}/dnf

%global pluginconfpath %{confdir}/plugins
%global py2pluginpath %{python_sitelib}/dnf-plugins
%global py3pluginpath %{python3_sitelib}/dnf-plugins

Name:		dnf
Version:	0.6.7
Release:	1%{?snapshot}%{?dist}
Summary:	Package manager forked from Yum, using libsolv as a dependency resolver
# For a breakdown of the licensing, see PACKAGE-LICENSING
License:	GPLv2+ and GPLv2 and GPL
URL:		https://github.com/rpm-software-management/dnf
# The Source0 tarball can be generated using following commands:
# git clone http://github.com/rpm-software-management/dnf.git
# cd dnf/package
# ./archive
# tarball will be generated in $HOME/rpmbuild/sources/
Source0:    http://rpm-software-management.fedorapeople.org/dnf-%{gitrev}.tar.xz
BuildArch:  noarch
BuildRequires:  cmake
BuildRequires:  gettext
BuildRequires:  python-bugzilla
BuildRequires:  python-sphinx
BuildRequires:  systemd
%if 0%{?fedora} >= 23
Requires:   python3-dnf = %{version}-%{release}
%else
Requires:   python-dnf = %{version}-%{release}
%endif
Requires(post):     systemd
Requires(preun):    systemd
Requires(postun):   systemd
%description
Package manager forked from Yum, using libsolv as a dependency resolver.

%package conf
Requires:   libreport-filesystem
Summary:    Configuration files for DNF.
%description conf
Configuration files for DNF.

%package -n dnf-yum
Conflicts:      yum
Requires:   dnf = %{version}-%{release}
Summary:    As a Yum CLI compatibility layer, supplies /usr/bin/yum redirecting to DNF.
%description -n dnf-yum
As a Yum CLI compatibility layer, supplies /usr/bin/yum redirecting to DNF.

%package -n python-dnf
Summary:    Python 2 interface to DNF.
BuildRequires:  pygpgme
BuildRequires:  pyliblzma
BuildRequires:  python2
BuildRequires:  python-hawkey >= %{hawkey_version}
BuildRequires:  python-iniparse
BuildRequires:  python-libcomps >= %{libcomps_version}
BuildRequires:  python-librepo >= %{librepo_version}
BuildRequires:  python-nose
BuildRequires:  rpm-python >= %{rpm_version}
Requires:   dnf-conf = %{version}-%{release}
Requires:   deltarpm
Requires:   pygpgme
Requires:   pyliblzma
Requires:   python-hawkey >= %{hawkey_version}
Requires:   python-iniparse
Requires:   python-libcomps >= %{libcomps_version}
Requires:   python-librepo >= %{librepo_version}
Requires:   rpm-plugin-systemd-inhibit
Requires:   rpm-python >= %{rpm_version}
Obsoletes:  dnf <= 0.6.4
%description -n python-dnf
Python 2 interface to DNF.

%package -n python3-dnf
Summary:    Python 3 interface to DNF.
BuildRequires:  python3
BuildRequires:  python3-devel
BuildRequires:  python3-hawkey >= %{hawkey_version}
BuildRequires:  python3-iniparse
BuildRequires:  python3-libcomps >= %{libcomps_version}
BuildRequires:  python3-librepo >= %{librepo_version}
BuildRequires:  python3-nose
BuildRequires:  python3-pygpgme
BuildRequires:  rpm-python3 >= %{rpm_version}
Requires:   dnf-conf = %{version}-%{release}
Requires:   deltarpm
Requires:   python3-hawkey >= %{hawkey_version}
Requires:   python3-iniparse
Requires:   python3-libcomps >= %{libcomps_version}
Requires:   python3-librepo >= %{librepo_version}
Requires:   python3-pygpgme
Requires:   rpm-plugin-systemd-inhibit
Requires:   rpm-python3 >= %{rpm_version}
Obsoletes:  dnf <= 0.6.4
%description -n python3-dnf
Python 3 interface to DNF.

%package automatic
Summary:    Alternative CLI to "dnf upgrade" suitable for automatic, regular execution.
BuildRequires:  systemd
Requires:   dnf = %{version}-%{release}
Requires(post):     systemd
Requires(preun):    systemd
Requires(postun):	systemd
%description automatic
Alternative CLI to "dnf upgrade" suitable for automatic, regular execution.

%prep
%setup -q -n dnf
rm -rf py3
mkdir ../py3
cp -a . ../py3/
mv ../py3 ./

%build
%cmake .
make %{?_smp_mflags}
make doc-man
pushd py3
%cmake -DPYTHON_DESIRED:str=3 -DWITH_MAN=0 .
make %{?_smp_mflags}
popd

%install
make install DESTDIR=$RPM_BUILD_ROOT
%find_lang %{name}
pushd py3
make install DESTDIR=$RPM_BUILD_ROOT
popd

mkdir -p $RPM_BUILD_ROOT%{pluginconfpath}
mkdir -p $RPM_BUILD_ROOT%{py2pluginpath}
mkdir -p $RPM_BUILD_ROOT%{py3pluginpath}/__pycache__
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/log
touch $RPM_BUILD_ROOT%{_localstatedir}/log/%{name}.log
%if 0%{?fedora} >= 23
ln -sr $RPM_BUILD_ROOT%{_bindir}/dnf-3 $RPM_BUILD_ROOT%{_bindir}/dnf
%else
ln -sr $RPM_BUILD_ROOT%{_bindir}/dnf-2 $RPM_BUILD_ROOT%{_bindir}/dnf
%endif
ln -sr $RPM_BUILD_ROOT%{_bindir}/dnf $RPM_BUILD_ROOT%{_bindir}/yum

%check
make ARGS="-V" test
pushd py3
make ARGS="-V" test
popd

%files -f %{name}.lang
%doc AUTHORS README.rst COPYING PACKAGE-LICENSING
%{_bindir}/dnf
%{_mandir}/man8/dnf.8.gz
%{_mandir}/man5/dnf.conf.5.gz
%config %{_sysconfdir}/bash_completion.d/dnf-completion.bash
%{_unitdir}/dnf-makecache.service
%{_unitdir}/dnf-makecache.timer
%{_tmpfilesdir}/dnf.conf

%files conf
%doc AUTHORS README.rst COPYING PACKAGE-LICENSING
%dir %{confdir}
%dir %{pluginconfpath}
%dir %{confdir}/protected.d
%config(noreplace) %{confdir}/dnf.conf
%config(noreplace) %{confdir}/protected.d/dnf.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%ghost %{_localstatedir}/log/hawkey.log
%ghost %{_localstatedir}/log/%{name}.log
%ghost %{_localstatedir}/log/%{name}.rpm.log
%ghost %{_localstatedir}/log/%{name}.plugin.log
%config %{_sysconfdir}/bash_completion.d/dnf-completion.bash
%{_sysconfdir}/libreport/events.d/collect_dnf.conf

%files -n dnf-yum
%doc AUTHORS README.rst COPYING PACKAGE-LICENSING
%{_bindir}/yum

%files -n python-dnf
%{_bindir}/dnf-2
%doc AUTHORS README.rst COPYING PACKAGE-LICENSING
%exclude %{python_sitelib}/dnf/automatic
%{python_sitelib}/dnf/
%ghost %{_sharedstatedir}/dnf
%dir %{py2pluginpath}

%files -n python3-dnf
%doc AUTHORS README.rst COPYING PACKAGE-LICENSING
%{_bindir}/dnf-3
%exclude %{python3_sitelib}/dnf/automatic
%{python3_sitelib}/dnf/
%ghost %{_sharedstatedir}/dnf
%dir %{py3pluginpath}
%dir %{py3pluginpath}/__pycache__

%files automatic
%doc AUTHORS COPYING PACKAGE-LICENSING
%{_bindir}/dnf-automatic
%config(noreplace) %{confdir}/automatic.conf
%{_mandir}/man8/dnf.automatic.8.gz
%{_unitdir}/dnf-automatic.service
%{_unitdir}/dnf-automatic.timer
%{python_sitelib}/dnf/automatic

%post
%systemd_post dnf-makecache.timer

%preun
%systemd_preun dnf-makecache.timer

%postun
%systemd_postun_with_restart dnf-makecache.timer

%post automatic
%systemd_post dnf-automatic.timer

%preun automatic
%systemd_preun dnf-automatic.timer

%postun automatic
%systemd_postun_with_restart dnf-automatic.timer

%changelog
* Tue Mar 17 2015 Michal Luscon <mluscon@redhat.com> 0.6.7-1
- 

* Tue Mar 17 2015 Michal Luscon <mluscon@redhat.com> 0.6.6-1
- first tito build


* Wed Feb 4 2015 Jan Silhan <jsilhan@redhat.com> - 0.6.4-1
- Adapt to librepo-1.7.13, metalink and mirrorlist are not loaded anymore when the repo is local. (Radek Holy)
- not raises value error when no metadata exist (Jan Silhan)
- Remove lock files during boot (RhBug:1154476) (Michal Luscon)
- doc: groups are ordered not categories (Jan Silhan)
- doc: added Package attributes to API (Jan Silhan)
- README: link to bug reporting guide (Jan Silhan)
- README: the official documentation is on readthedoc (Jan Silhan)
- i18n: unicode encoding does not throw error (RhBug:1155877) (Jan Silhan)
- conf: added minrate repo option (Related:RhBug:1175466) (Jan Silhan)
- conf: added timeout repo option (RhBug:1175466) (Jan Silhan)
- doc: api_queries: add 'file' filter description (RhBug:1186461) (Igor Gnatenko)
- doc: documenting enablegroups (Jan Silhan)
- log: printing metadata timestamp (RhBug:1170156) (Jan Silhan)
- base: setup default cachedir value (RhBug:1184943) (Michal Luscon)
- orders groups/environments by display_order tag (RhBug:1177002) (Jan Silhan)
- no need to call create_cmdline_repo (Jan Silhan)
- base: package-spec matches all packages which the name glob pattern fits (RhBug:1169165) (Michal Luscon)
- doc: move dnf.conf to appropriate man page section (RhBug:1167982) (Michal Luscon)
- tests: add test for blocking process lock (Michal Luscon)
- lock: fix several race conditions in process lock mechanism (Michal Luscon)
- base: use blocking process lock during download phase (RhBug:1157233) (Michal Luscon)
- Update the Source0 generation commands in dnf.spec.in file (Parag Nemade)
- Enhancement to dnf.spec.in file which follows current fedora packaging guidelines (Parag Nemade)
- doc: add some examples and documentation of the core use case (RhBug:1138096) (Radek Holy)
- bash-completion: enable downgrading packages for local files (RhBug:1181189) (Igor Gnatenko)
- group: prints plain package name when package not in any repo (RhBug:1181397) (Jan Silhan)
- spec: own __pycache__ for python 3 (Igor Gnatenko)
- changed hawkey.log dir to /var/log (RhBug:1175434) (Jan Silhan)
- bash-completion: handle sqlite errors (Igor Gnatenko)
- use LANG=C when invoking 'dnf help' and 'sed' with regular expressions (Jakub Dorňák)
- spec: own __pycache__ directory for py3 (Igor Gnatenko)
- doc: mentioning Install command accepts path to local rpm package (Jan Silhan)
- groups: in erase and install cmd non-existent group does not abort transaction (Jan Silhan)
- doc: running tests in README (Jan Silhan)
- api: transaction: added install_set and remove_set (RhBug:1162887) (Jan Silhan)
- cosmetic: fixed some typos in documentation (Jan Silhan)
- groups: environments described after @ sign works (RhBug:1156084) (Jan Silhan)
- own /etc/dnf/protected.d (RhBug:1175098) (Jan Silhan)
- i18n: computing width of char right (RhBug:1174136) (Jan Silhan)
- cosmetic: renamed _splitArg -> _split_arg (Jan Silhan)
- conf: removed include name conflict (RhBug:1055910) (Jan Silhan)
- output: removed unpredictible decision based on probability introduced in ab4d2c5 (Jan Silhan)
- output: history list is not limited to 20 records (RhBug:1155918) (Jan Silhan)
- doc: referenced forgotten bug fix to release notes (Jan Silhan)
- cosmetic: doc: removed duplicated word (Jan Silhan)
- doc: described unavailable package corner case with skip_if_unavailable option (RhBug:1119030) (Jan Silhan)
- log: replaced size with maxsize directive (RhBug:1177394) (Jan Silhan)
- spec: fixed %ghost log file names (Jan Silhan)

* Mon Dec 8 2014 Jan Silhan <jsilhan@redhat.com> - 0.6.3-2
- logging: reverted naming from a6dde81

* Mon Dec 8 2014 Jan Silhan <jsilhan@redhat.com> - 0.6.3-1
- transifex update (Jan Silhan)
- bash-completion: don't query if we trying to use local file (RhBug:1153543) (Igor Gnatenko)
- bash-completion: fix local completion (RhBug:1151231) (Igor Gnatenko)
- bash-completion: use sqlite cache from dnf-plugins-core (Igor Gnatenko)
- base: output a whole list of installed packages with glob pattern (RhBug:1163063) (Michal Luscon)
- cli: _process_demands() does not respect --caheonly (RhBug:1151854) (Michal Luscon)
- new authors added (Jan Silhan)
- install: allow installation of provides with glob (Related:RhBug:1148353) (Michal Luscon)
- tests: removed mock patch for _, P_ (Jan Silhan)
- fixed error summary traceback (RhBug:1151740) (Jan Silhan)
- doc: swap command alternative mentioned (RhBug:1110780) (Jan Silhan)
- base: package_reinstall works only with the same package versions (Jan Silhan)
- base: package_install allows install different arch of installed package (Jan Silhan)
- base: package_downgrade prints message on failure (Jan Silhan)
- base: package_upgrade does not reinstall or downgrade (RhBug:1149972) (Jan Silhan)
- groups: searches also within localized names (RhBug:1150474) (Jan Silhan)
- Run tests with C locales. (Daniel Mach)
- Adds new motd emitter for dnf-automatic (RhBug:995537) (Kushal Das)
- Fix wrong cache directory path used to clean up binary cache (Satoshi Matsumoto)
- fix: traceback in history info <name> (RhBug: 1149952) (Tim Lauridsen)
- logging: added logrotate script for hawkey.log (RhBug:1149350) (Jan Silhan)
- output: renamed displayPkgsInGroups (Jan Silhan)
- logging: renamed log files (RhBug:1074715)" (Jan Silhan)
- comps: Environment differentiates optional and mandatory groups (Jan Silhan)
- group info handles environments (RhBug:1147523) (Jan Silhan)
- deltarpm enabled by default (RhBug:1148208) (Jan Silhan)
- doc: deplist command (Jan Silhan)
- doc: minor fixes + repo references changed (Jan Silhan)
- spec: requires rpm-plugin-systemd-inhibit (RhBug:1109927) (Jan Silhan)

* Fri Oct 3 2014 Jan Silhan <jsilhan@redhat.com> - 0.6.2-1
- transifex update (Jan Silhan)
- refactor: move MakeCacheCommand out into its own file. (Ales Kozumplik)
- api: add dnf.cli.CliError. (Ales Kozumplik)
- Update user_faq.rst (Stef Krie)
- Make --refresh play nice with lazy commands. (Ales Kozumplik)
- bash-completion: more faster completing install/remove (Igor Gnatenko)
- bash-completion: complete 'clean|groups|repolist' using help (Igor Gnatenko)
- Allow some commands to use stale metadata. (RhBug:909856) (Ales Kozumplik)
- does not install new pkgs when updating from local pkgs (RhBug:1134893) (Jan Silhan)
- doesn't upgrade packages by installing local packages (Related:RhBug:1138700) (Jan Silhan)
- refactor: repo: separate concepts of 'expiry' and 'sync strategy'. (Ales Kozumplik)
- fix: dnf.cli.util.* leaks file handles. (Ales Kozumplik)
- remove: YumRPMTransError. (Ales Kozumplik)
- rename: Base's runTransaction -> _run_transaction(). (Ales Kozumplik)
- drop unused parameter of Base.verify_transaction(). (Ales Kozumplik)
- bash-completion: new completion from scratch (RhBug:1070902) (Igor Gnatenko)
- py3: add queue.Queue to pycomp. (Ales Kozumplik)
- locking: store lockfiles with the resource they are locking. (RhBug:1124316) (Ales Kozumplik)
- groups: marks reason 'group' for packages that have no record yet (RhBug:1136584) (Jan Silhan)
- goal: renamed undefined name variable (Jan Silhan)
- refactor: split out and clean up the erase command. (Ales Kozumplik)
- py3: fix traceback in fmtColumns() on a non-subscriptable 'columns'. (Ales Kozumplik)
- groups: allow erasing depending packages on remove (RhBug:1135861) (Ales Kozumplik)
- history: fixed wrong set operation (RhBug:1136223) (Jan Silhan)
- base: does not reinstall pkgs from local rpms with install command (RhBug:1122617) (Jan Silhan)
- refactor: crypto: drop the integer keyid representation altogether. (Ales Kozumplik)
- crypto: fix importing rpmfusion keys. (RhBug:1133830) (Ales Kozumplik)
- refactor: crypto: Key is a class, not an "info" dict. (Ales Kozumplik)
- repos: fix total downloaded size reporting for cached packages. (RhBug:1121184) (Ales Kozumplik)

* Thu Aug 28 2014 Jan Silhan <jsilhan@redhat.com> - 0.6.1-1
- packaging: add dnf-yum. (Ales Kozumplik)
- cli: added plugins missing hint (RhBug:1132335) (Jan Silhan)
- using ts.addReinstall for package reinstallation (RhBug:1071854) (Jan Silhan)
- Add history redo command. (Radek Holy)
- Add a TransactionConverter class. (Radek Holy)
- bash-completion: complete `help` with commands (Igor Gnatenko)
- bash-completion: generate commands dynamically (Igor Gnatenko)
- base: group_install accepts glob exclude names (RhBug:1131969) (Jan Silhan)
- README: changed references to new repo location (Jan Silhan)
- transifex update (Jan Silhan)
- syntax: fixed indentation (Jan Silhan)
- removed lt.po which was accidentally added in c2e9b39 (Jan Silhan)
- lint: fix convention violations in the new source files (Radek Holy)
- Fix setting of the resolving demand for repo-pkgs command. (Radek Holy)
- Add repository-packages remove-or-distro-sync command. (RhBug:908764) (Radek Holy)
- fix: traceback that GroupPersistor._original might not exist. (RhBug:1130878) (Ales Kozumplik)
- pycomp: drop to_ord(). (Ales Kozumplik)
- refactor: crypto.keyids_from_pubring() using _extract_signing_subkey(). (Ales Kozumplik)
- fix: another 32-bit hex() problem in crypto. (Ales Kozumplik)
- remove: pgpmsg.py. (Ales Kozumplik)
- replace the whole of pgpmsg.py with gpgme and a dummy context. (Ales Kozumplik)
- cosmetic: sort methods of Repo according to the coding standard. (Ales Kozumplik)
- Fix dnf.crypto.keyinfo2keyid(). (Ales Kozumplik)
- util: get rid of an inconvenient 'default_handle' constant. (Ales Kozumplik)
- simplify misc.import_key_to_pubring()'s signature. (Ales Kozumplik)
- cleanup: header of dnf.yum.pgpmsg. (Ales Kozumplik)
- crypto: add crypto.retrieve() and drop Base._retrievePublicKey() (Ales Kozumplik)
- cosmetic: order of functions in dnf.crypto. (Ales Kozumplik)
- unicode: fixed locale.format error (RhBug:1130432) (Jan Silhan)
- remove: misc.valid_detached_sig(). (Ales Kozumplik)
- tests: some tests for dnf.crypto. (Ales Kozumplik)
- crypto: use pubring_dir() context manager systematically. (Ales Kozumplik)
- Drop unused argument from getgpgkeyinfo(). (Ales Kozumplik)
- remove: Base._log_key_import(). (Ales Kozumplik)
- doc: cosmetic: conf_ref: maintain alphabetical order of the options. (Ales Kozumplik)
- crypto: document crypto options for repo. (Ales Kozumplik)
- crypto: fixup procgpgkey() to work with Py3 bytes. (Ales Kozumplik)
- dnf.util.urlopen(): do not create unicode streams for Py3 and bytes for Py2 by default. (Ales Kozumplik)
- lint: delinting of the repo_gpgcheck patchset. (Ales Kozumplik)
- Add CLI parts to let the user confirm key imports. (RhBug:1118236) (Ales Kozumplik)
- gpg: make key decoding work under Py3. (Ales Kozumplik)
- crypto: add dnf.crypto and fix things up so untrusted repo keys can be imported. (Ales Kozumplik)
- transifex update (Jan Silhan)
- syntax: fixed indentation (Jan Silhan)
- packaging: pygpgme is a requirement. (Ales Kozumplik)
- remove: support for gpgcakey gets dropped for now. (Ales Kozumplik)
- repo: smarter _DetailedLibrepoError construction. (Ales Kozumplik)
- repo: nicer error message on librepo's perform() failure. (Ales Kozumplik)
- get_best_selector returns empty selector instead of None (Jan Silhan)
- packaging: add automatic's systemd unit files. (RhBug:1109915) (Ales Kozumplik)
- automatic: handle 'security' update_cmd. (Ales Kozumplik)

* Tue Aug 12 2014 Aleš Kozumplík <ales@redhat.com> - 0.6.0-1
- lint: fix convention violations in the new source files (Radek Holy)
- Add "updateinfo [<output>] [<availability>] security" command. (RhBug:850912) (Radek Holy)
- Add "updateinfo [<output>] [<availability>] bugfix" command. (Radek Holy)
- Add "updateinfo [<output>] [<availability>] enhancement" command. (Radek Holy)
- Add "updateinfo [<output>] [<availability>] [<package-name>...]" command. (Radek Holy)
- Add "updateinfo [<output>] [<availability>] [<advisory>...]" command. (Radek Holy)
- Add "updateinfo [<output>] all" command. (Radek Holy)
- Add "updateinfo [<output>] updates" command. (Radek Holy)
- Add "updateinfo [<output>] installed" command. (Radek Holy)
- Add "-v updateinfo info" command. (Radek Holy)
- Add "updateinfo info" command. (Radek Holy)
- Add "updateinfo list" command. (Radek Holy)
- Add "updateinfo available" command. (Radek Holy)
- Add "updateinfo summary" command. (Radek Holy)
- Add basic updateinfo command. (Radek Holy)
- test: add updateinfo to the testing repository (Radek Holy)
- test: support adding directory repos to Base stubs (Radek Holy)
- test: really don't break other tests with the DRPM fixture (Radek Holy)
- Load UpdateInfo.xml during the sack preparation. (Radek Holy)
- Add Repo.updateinfo_fn. (Radek Holy)
- lint: add Selector calls to false positives, it's a hawkey type. (Ales Kozumplik)
- removed recursive calling of ucd in DownloadError (Jan Silhan)
- does not throw error when selector is empty (RhBug:1127206) (Jan Silhan)
- remove etc/version-groups.conf, not used. (Ales Kozumplik)
- lint: dnf.conf.parser (Ales Kozumplik)
- rename: dnf.conf.parser.varReplace()->substitute() (Ales Kozumplik)
- pycomp: add urlparse/urllib.parser. (Ales Kozumplik)
- move: dnf.yum.parser -> dnf.conf.parser. (Ales Kozumplik)
- packaging: add dnf-automatic subpackage. (Ales Kozumplik)
- doc: properly list the authors. (Ales Kozumplik)
- automatic: add documentation, including dnf.automatic(8) man page. (Ales Kozumplik)
- dnf-automatic: tool supplying the yum-cron functionality. (Ales Kozumplik)
- doc: cosmetic: fixed indent in proxy directive (Jan Silhan)
- include directive support added (RhBug:1055910) (Jan Silhan)
- refactor: move MultiCallList to util. (Ales Kozumplik)
- cli: do not output that extra starting newline in list_transaction(). (Ales Kozumplik)
- refactor: extract CLI cachedir magic to cli.cachedir_fit. (Ales Kozumplik)
- transifex update (Jan Silhan)
- move: test_output to tests/cli. (Ales Kozumplik)
- refactor: move Term into its own module. (Ales Kozumplik)
- refactoring: cleanup and linting in dnf.exceptions. (Ales Kozumplik)
- lint: test_cli.py (Ales Kozumplik)
- lint: rudimentary cleanups in tests.support. (Ales Kozumplik)
- refactor: loggers are module-level variables. (Ales Kozumplik)
- groups: promote unknown-reason installed packages to 'group' on group install. (RhBug:1116666) (Ales Kozumplik)
- c82267f refactoring droppped plugins.run_transaction(). (Ales Kozumplik)
- cli: sort packages in the transaction summary. (Ales Kozumplik)
- refactor: cli: massively simplify how errors are propagated from do_transaction(). (Ales Kozumplik)
- groups: rearrange things in CLI so user has to confirm the group changes. (Ales Kozumplik)
- groups: commiting the persistor data should only happen at one place. (Ales Kozumplik)
- groups: visualizing the groups transactions. (Ales Kozumplik)
- Add dnf.util.get_in() to navigate nested dicts with sequences of keys. (Ales Kozumplik)
- group persistor: generate diffs between old and new DBs. (Ales Kozumplik)
- Better quoting in dnf_pylint. (Ales Kozumplik)
- lint: logging.py. (Ales Kozumplik)
- Do not print tracebacks to the tty on '-d 10' (RhBug:1118272) (Ales Kozumplik)
- search: do not double-report no matches. (Ales Kozumplik)
- refactor: move UpgradeToCommand to its own module. (Ales Kozumplik)

* Mon Jul 28 2014 Aleš Kozumplík <ales@redhat.com> - 0.5.5-1
- packaging: also add pyliblzma to BuildRequires. (Ales Kozumplik)
- essential cleanup in dnf.yum.misc, removing a couple of functions too. (Ales Kozumplik)
- remove: Base.findDeps and friends. (Ales Kozumplik)
- Make pyliblzma a requriement. (RhBug:1123688) (Ales Kozumplik)
- whole user name can contain non-ascii chars (RhBug:1121280) (Jan Silhan)
- Straighten up the exceptions when getting a packages header. (RhBug:1122900) (Ales Kozumplik)
- tests: refactor: rename test_resource_path() -> resource_path() and use it more. (Ales Kozumplik)
- transifex update (Jan Silhan)
- remove: conf.commands. (Ales Kozumplik)
- proxy username and password, for both CLI and API. (RhBug:1120583) (Ales Kozumplik)
- conf: only 'main' is a reserved section name. (Ales Kozumplik)
- refactoring: cleanup a couple of lint warnings in base.py. (Ales Kozumplik)
- refactoring: move repo reading implementation out of dnf.Base. (Ales Kozumplik)
- refactor: repo_setopts is a CLI thing and doesn't belong to Base. (Ales Kozumplik)
- refactor: move cleanup methods to dnf.cli.commands.clean. (Ales Kozumplik)
- depsolving: doesn't install both architectures of pkg by filename (RhBug:1100946) (Jan Silhan)
- refactor: put CleanCommand in its own module. (Ales Kozumplik)
- cli: avoid 'Error: None' output on malformed CLI commands. (Ales Kozumplik)
- remove the special SIGQUIT handler. (Ales Kozumplik)
- api: In Repo(), cachedir is a required argument. (Ales Kozumplik)
- api: better describe how Repos should be created, example. (RhBug:1117789) (Ales Kozumplik)
- Base._conf lasts the lifetime of Base and can be passed via constructor. (Ales Kozumplik)
- doc: faq: having Yum and DNF installed at the same time. (Ales Kozumplik)
- remove: protected_packages config option, it has been ignored. (Ales Kozumplik)
- fix: misleading error message when no repo is enabled. (Ales Kozumplik)

* Wed Jul 16 2014 Aleš Kozumplík <ales@redhat.com> - 0.5.4-1
- pkg name from rpm transaction callback is in Unicode (RhBug:1118796) (Jan Silhan)
- packaging: python3-dnf depends on dnf. (RhBug:1119032) (Ales Kozumplik)
- Ship /usr/bin/dnf-3 to run DNF under Py3. (RhBug:1117678) (Ales Kozumplik)
- packaging: own /etc/dnf/plugins. (RhBug:1118178) (Ales Kozumplik)
- fix: pluginconfpath is a list. (Ales Kozumplik)
- cosmetic: use classmethod as a decorator in config.py. (Ales Kozumplik)
- cleanup: imports in dnf.cli.output (Ales Kozumplik)
- lint: straightforward lint fixes in dnf.cli.output. (Ales Kozumplik)
- Repo.__setattr__ has to use the parsed value. (Ales Kozumplik)
- Repo priorities. (RhBug:1048973) (Ales Kozumplik)
- repo: simplify how things are propagated to repo.hawkey_repo. (Ales Kozumplik)
- refactor: concentrate Repo.hawkey_repo construction in Repo.__init__(). (Ales Kozumplik)
- bash-completion: Update command and option lists, sort in same order as --help (Ville Skyttä)
- bash-completion: Use grep -E instead of deprecated egrep (Ville Skyttä)
- output: fixed identation of info command output (Jan Silhan)
- i18n: calculates right width of asian utf-8 strings (RhBug:1116544) (Jan Silhan)
- transifex update + renamed po files to Fedora conventions (Jan Silhan)
- remove: CLI: --randomwait (Ales Kozumplik)
- cli: fix: --installroot has to be used with --releasever (RhBug:1117293) (Ales Kozumplik)
- Base.reset(goal=True) also resets the group persistor (RhBug:1116839) (Ales Kozumplik)
- tests: fix failing DistroSync.test_distro_sync(). (Ales Kozumplik)
- logging: RPM transaction markers are too loud. (Ales Kozumplik)
- logging: silence drpm a bit. (Ales Kozumplik)
- logging: put timing functionality into one place. (Ales Kozumplik)
- repolist: fix traceback with disabled repos. (RhBug:1116845) (Ales Kozumplik)
- refactor: cleanups in repolist. (Ales Kozumplik)
- lint: remove some unused imports. (Ales Kozumplik)
- cli: break out the repolsit command into a separate module. (Ales Kozumplik)
- does not crash with non-ascii user name (RhBug:1108908) (Jan Silhan)
- doc: document 'pluginpath' configuration option. (RhBug:1117102) (Ales Kozumplik)
- Spelling fixes (Ville Skyttä)
- cli: Fix software name in --version help (Ville Skyttä)
- doc: ip_resolve documented at two places. remove one. (Ales Kozumplik)

* Thu Jul 3 2014 Aleš Kozumplík <ales@redhat.com> - 0.5.3-1
- packaging: bump hawkey dep to 0.4.17. (Ales Kozumplik)
- api: remove Base.select_group(). (Ales Kozumplik)
- tests: cleanup our base test case classes a bit. (Ales Kozumplik)
- Add DNF itself among the protected packages. (Ales Kozumplik)
- api: plugins: add the resolved() hook. (Ales Kozumplik)
- api: expose Transaction introspecting in the API. (RhBug:1067156) (Ales Kozumplik)
- api: add basic documentation for dnf.package.Package. (Ales Kozumplik)
- tests: cosmetic: conf.protected_packages is ignored, drop it in FakeConf. (Ales Kozumplik)
- cli: simplify exception handling more. (Ales Kozumplik)
- Fixed a minor typo in user_faq - 'intall' should be 'install' (Martin Preisler)
- fixed encoding of parsed config line (RhBug:1110800) (Jan Silhan)
- syntax: replaced tab with spaces (Jan Silhan)
- doc: acknowledge the existence of plugins on the man page (RhBug:1112669) (Ales Kozumplik)
- improve the 'got root?' message of why a transaction couldn't start. (RhBug:1111569) (Ales Kozumplik)
- traceback in Base.do_transaction. to_utf8() is gone since 06fb280. (Ales Kozumplik)
- fix traceback from broken string formatting in _retrievePublicKey(). (RhBug:1111997) (Ales Kozumplik)
- doc: replace Yum with DNF in command_ref.rst (Viktor Ashirov)
- Fix a missing s in the title (mscherer)
- api: add dnf.rpm.detect_releasever() (Ales Kozumplik)
- Detect distroverpkg from 'system-release(release)' (RhBug:1047049) (Ales Kozumplik)
- bulid: add dnf/conf to cmake. (Ales Kozumplik)
- lint: clean up most lint messages in dnf.yum.config (Ales Kozumplik)
- remove: couple of dead-code methods in dnf.yum.config. (Ales Kozumplik)
- api: document client's responsibility to preset the substitutions. (RhBug:1104757) (Ales Kozumplik)
- move: rpmUtils -> rpm. (Ales Kozumplik)
- refactor: move yumvar out into its proper module dnf.conf.substitutions. (Ales Kozumplik)
- refactor: turn dnf.conf into a package. (Ales Kozumplik)
- doc: api_base.rst pointing to nonexistent method. (Ales Kozumplik)
- remove: some logging from Transaction.populate_rpm_ts(). (Ales Kozumplik)
- Update cli_vs_yum.rst (James Pearson)
- api: doc: queries relation specifiers, with an example. (RhBug:1105009) (Ales Kozumplik)
- doc: phrasing in ip_resolve documentation. (Ales Kozumplik)
- cli: refactored transferring cmdline options to conf (Jan Silhan)
- cli: added -4/-6 option for using ipv4/ipv6 connection (RhBug:1093420) (Jan Silhan)
- cosmetic: empty set inicialization (Jan Silhan)
- repo: improve the RepoError message to include URL. (Ales Kozumplik)
- remove: dnf.yum.config.writeRawRepoFile(). (Ales Kozumplik)
- remove: bunch of (now) blank config options. (Ales Kozumplik)
- removed unique function (Jan Silhan)
- tests: mock.assert_has_calls() enforces its iterable arguments in py3.4. (Ales Kozumplik)
- logging: improve how repolist logs the total number of packages. (Ales Kozumplik)
- logging: Base.close() should not log to the terminal. (Ales Kozumplik)

* Wed May 28 2014 Aleš Kozumplík <ales@redhat.com> - 0.5.2-1
- doc: packaging: add license block to each .rst. (Ales Kozumplik)
- cosmetic: replaced yum with dnf in comment (Jan Silhan)
- takes non-ascii cmd line input (RhBug:1092777) (Jan Silhan)
- replaced 'unicode' conversion functions with 'ucd' (RhBug:1095861) (Jan Silhan)
- using write_to_file py2/py3 compatibility write function (Jan Silhan)
- encoding: all encode methods are using utf-8 coding instead of default ascii (Jan Silhan)
- fixed rpmbuild warning of missing file (Jan Silhan)
- transifex update (Jan Silhan)
- fixed typos in comments (Jan Silhan)
- Drop --debugrepodata and susetags generation with it. (Ales Kozumplik)
- doc: document --debugsolver. (Ales Kozumplik)
- fix: 'dnf repo-pkgs' failures (RhBug:1092006) (Radek Holy)
- lint: make dnf_pylint take '-s' that suppresses line/column numbers. (Ales Kozumplik)
- doc: cli_vs_yum: we do not promote installs to the obsoleting package. (RhBug:1096506) (Ales Kozumplik)
- dealing with installonlies, we always need RPMPROB_FILTER_OLDPACKAGE (RhBug:1095580) (Ales Kozumplik)
- transifex update (Jan Silhan)
- arch: recognize noarch as noarch's basearch. (RhBug:1094594) (Ales Kozumplik)
- pylint: clean up dnf.repo. (Ales Kozumplik)
- sslverify: documentation and bumped librepo require. (Ales Kozumplik)
- repos: support sslverify setting. (RhBug:1076045) (Ales Kozumplik)
- search: exact matches should propagate higher. (RhBug:1093888) (Ales Kozumplik)
- refactor: concentrate specific search functionality in commands.search. (Ales Kozumplik)
- refactor: SearchCommand in its own file. (Ales Kozumplik)
- pylint: fix around one hundred pylint issues in dnf.base. (Ales Kozumplik)
- pylint: add simple pylint script (Ales Kozumplik)
- autoerase: write out the debugdata used to calculate redundant packages. (Ales Kozumplik)
- cosmetic: fix pylint comment in test_group.py. (Ales Kozumplik)
- refactor: err_mini_usage() is public. (Ales Kozumplik)
- refactor: fix several pylint errors in dnf.cli.commands.group. (Ales Kozumplik)
- fix: 'dnf remove' is deprecated so autoremove should be autoerase. (Ales Kozumplik)
- doc: command_ref: remove the deprecated aliases from the initial list. (Ales Kozumplik)
- Add autoremove command. (RhBug:963345) (Ales Kozumplik)
- refactor: Base.push_userinstalled() is public. (Ales Kozumplik)
- Remove sudo from dnf-completion.bash RhBug:1073457 (Elad Alfassa)
- exclude switch takes <package-spec> as a parameter (Jan Silhan)
- using nevra glob query during list command (RhBug:1083679) (Jan Silhan)
- removed rpm.RPMPROB_FILTER_REPLACEOLDFILES filter flag (Jan Silhan)
- test: changed tests according to new distro-sync behavior (Jan Silhan)
- packaging: cosmetic: copyright years in bin/dnf. (Ales Kozumplik)
- bin/dnf: run the python interpreter with -OO. (Ales Kozumplik)

* Fri May 2 2014 Aleš Kozumplík <ales@redhat.com> - 0.5.1-1
- drpm: output stats (RhBug:1065882) (Ales Kozumplik)
- refactor: architectures. (Ales Kozumplik)
- cli: be lot less verbose about dep processing. (Ales Kozumplik)
- groups: do not error out if group install/remove produces no RPM transaction. (Ales Kozumplik)
- fix: do not traceback on comps remove operations if proper pkg reasons can not be found. (Ales Kozumplik)
- fix: tracebacks in 'group remove ...' (Ales Kozumplik)
- groups: move all the logic of persistor saving from main.py to Base. (Ales Kozumplik)
- groups: auto-saving the groups persistor. (RhBug:1089864) (Ales Kozumplik)
- transifex update (Jan Silhan)
- remove: profiling code from cli.main. (Ales Kozumplik)
- remove: removal of dead code (Miroslav Suchý)
- doc: changes to rhbug.py to work on readthedocs.org. (Ales Kozumplik)
- doc: build the documentation without any dependencies (on DNF or anything else). (Ales Kozumplik)
- doc: make clear where one should expect bin/dnf (Miroslav Suchý)
- abrt: disable abrt for 'dnf makecache timer' run from systemd.service. (RhBug:1081753) (Ales Kozumplik)
- remove: stray itertools import from group.py. (Ales Kozumplik)

* Wed Apr 23 2014 Aleš Kozumplík <ales@redhat.com> - 0.5.0-1
- doc: fix formatting in api_cli.rst. (Ales Kozumplik)
- doc: document operation of 'group upgrade'. (Ales Kozumplik)
- comps: ensure only packages of 'group' reason get deleted on 'group erase'. (Ales Kozumplik)
- comps: store 'group' reason when installing a group-membering package. (Ales Kozumplik)
- Override Goal.get_reason(). (Ales Kozumplik)
- Add dnf.goal.Goal deriving from hawkey.Goal. (Ales Kozumplik)
- fix: encoding of yumdb directory names in py3. (Ales Kozumplik)
- tests: clean up the functions that load seeded comps a bit. (Ales Kozumplik)
- remove: cli._*aybeYouMeant(). (Ales Kozumplik)
- simplify groups/envs API methods in Base a lot. (Ales Kozumplik)
- tests: add test for Base._translate_comps_pkg_types() (Ales Kozumplik)
- refactor: move the group listing etc. methods() away from Base into GroupCommand. (Ales Kozumplik)
- api: add group.upgrade opration to Base and CLI (RhBug:1029022) (Ales Kozumplik)
- remove: OriginalGroupPersistor. (Ales Kozumplik)
- groups: store format version of the groups db. (Ales Kozumplik)
- groups: saving the persistent data. (Ales Kozumplik)
- refactor: extract out the transactioning part of _main(). (Ales Kozumplik)
- groups: Integrate the redone componenets with Base. (Ales Kozumplik)
- Add comps Solver. (Ales Kozumplik)
- groups: redo the GroupPersistor class. (Ales Kozumplik)
- doc: faq: why we don't check for root. (RhBug:1088166) (Ales Kozumplik)
- cosmetic: reordered import statements (Jan Silhan)
- added --refresh option (RhBug:1064226) (Jan Silhan)
- added forgotten import (Jan Silhan)
- fixed import errors after yum/i18n.py removal (Jan Silhan)
- removed to_utf8 from yum/i18n.py (Jan Silhan)
- removed to_str from yum/i18n.py (Jan Silhan)
- removed utf8_text_fill from yum/i18n.py (Jan Silhan)
- removed utf8_width from yum/i18n.py (Jan Silhan)
- removed utf8_width_fill from yum/i18n.py (Jan Silhan)
- removed to_unicode from yum/i18n.py (Jan Silhan)
- make all strings unicode_literals implicitly (Jan Silhan)
- moved _, P_ to dnf/i18n.py (Jan Silhan)
- removed utf8_valid from yum/i18n.py (Jan Silhan)
- removed str_eq from yum/i18n.py (Jan Silhan)
- removed exception2msg from yum/i18n.py (Jan Silhan)
- removed dummy_wrapper from yum/i18n.py (Jan Silhan)
- cosmetics: leave around the good things from 660c3e5 (documentation, UT). (Ales Kozumplik)
- Revert "fix: provides are not recognized for erase command. (RhBug:1087063)" (Ales Kozumplik)
- fix: provides are not recognized for erase command. (RhBug:1087063) (Ales Kozumplik)
- test: fix UsageTest test, so it work without dnf is installed on the system PEP8 cleanup (Tim Lauridsen)
- cleanup: getSummary() and getUsage() can be dropped entirely now. (Ales Kozumplik)
- test: use Command.usage & Command.summary API in unittest (Tim Lauridsen)
- show plugin commands in separate block api: add new public Command.usage & Command.summary API cleanup: make Commands (Tim Lauridsen)
- tests: move libcomps test to a separate test file. (Ales Kozumplik)
- refactor: put DistoSyncCommand into its own file (Tim Lauridsen)
- refactor: commands.group: _split_extcmd is a static method. (Ales Kozumplik)
- GroupsCommand: make the way comps are searched more robust. (RhBug:1051869) (Ales Kozumplik)
- tests: move GroupCommand tests to a more proper place. (Ales Kozumplik)
- fix leak: Base.__del__ causes GC-uncollectable circles. (Ales Kozumplik)
- gruops: 'list' and similar commands should run without root. (RhBug:1080331) (Ales Kozumplik)
- refactor: conf is given to Output on instantiation. (Ales Kozumplik)
- remove: Command.done_command_once and Command.hidden. (Ales Kozumplik)
- [doc] improve documentation of '--best' (RhBug:1084553) (Ales Kozumplik)
- api: Command.base and Command.cli are API attributes. (Ales Kozumplik)
- demands: similarly to 78661a4, commands should set the exit success_exit_status directly. (Ales Kozumplik)
- demands: commands requiring resolving dymamically need to set the demand now. (Ales Kozumplik)
- doc: typo in group doc. (RhBug:1084139) (Ales Kozumplik)
- api: Base.resolve() takes allow_erasing. (RhBug:1073859) (Ales Kozumplik)
- refactor: OptionParser._checkAbsInstallRoot is static. (Ales Kozumplik)
- option_parser: remove base dependency. (Ales Kozumplik)
- move: dnf.cli.cli.OptionParser -> dnf.cli.option_parser.OptionParser. (Ales Kozumplik)
- doc: 'clean packages' incorrectly mentions we do not delete cached packages. (RhBug:1083767) (Ales Kozumplik)
- fix: TypeError in dnf history info <id> (RHBug: #1082230) (Tim Lauridsen)
- Start new version: 0.5.0. (Ales Kozumplik)
- remove: instance attrs of Base, namely cacheonly. (Ales Kozumplik)
- tests: remove: support.MockCli. (Ales Kozumplik)
- tests: fix locale independence. (Radek Holy)
- cleanups in cli.OptionParser. (Ales Kozumplik)
- fix: PendingDeprecationWarning from RPM in gpgKeyCheck(). (Ales Kozumplik)
- api: add Cli.demands.root_user (RhBug:1062889) (Ales Kozumplik)
- api: add Cli.demands and Command.config() to the API (RhBug:1062884) (Ales Kozumplik)
- Integrate DemandSheet into CLI. (Ales Kozumplik)
- Command.configure() takes the command arguments like run(). (Ales Kozumplik)
- Add dnf.cli.demand.DemandSheet. (Ales Kozumplik)
- remove: dead code for deplist, version and check-rpmdb commands. (Ales Kozumplik)
- sync with transifex (Jan Silhan)
- removed _enc method that did nothing without specspo (Jan Silhan)
- fixed local reinstall error (Jan Silhan)
- Fix Term.MODE setting under Python 3 in case of incapable tty stdout. (Radek Holy)
- tests: move Term tests to better file. (Radek Holy)
- refactor: move ReinstallCommand in its own module. (Ales Kozumplik)
- rename: yumbase (case insensitive) -> base. (Ales Kozumplik)
- fixed py3 error thrown by search command (Jan Silhan)
- fixed wrong named variable (Jan Silhan)
- fixed local downgrade error (Jan Silhan)
- doc: fix Package references that are ambiguous now. (Ales Kozumplik)
- fix: resource leak in yum.misc.checksum() under py3. (Ales Kozumplik)
- fix: leak: couple of files objects left open. (Ales Kozumplik)
- fix PendingDepreaction warning from rpm in _getsysver(). (Ales Kozumplik)
- repo: Repo.cachedir is not a list. (Ales Kozumplik)
- api: add Base.package_install et al. and Base.add_remote_rpm(). (RhBug:1079519) (Ales Kozumplik)
- tests: fix tests broken under foreign locale after 32818b2. (Ales Kozumplik)
- refactor: move install, downgrade and upgrade commands into separate modules. (Ales Kozumplik)
- tests: refactor: make Term tests more isolated. (Radek Holy)
- tests: fix terminfo capability independence. (Radek Holy)
- api: explain that Base is a context manager with a close(). (Ales Kozumplik)
- cosmetic: move stuff around in comps. (Ales Kozumplik)
- api: groups: add comps.Package, add group.package_iter(). (RhBug:1079932) (Ales Kozumplik)
- fixed installation of conflicted packages (RhBug:1061780) (Jan Silhan)
- removed never executed code based on _ts_saved_file variable (Jan Silhan)
- added logrotate script and ownership of log files to dnf (RhBug:1064211) (Jan Silhan)
- fixed: highlight characters broken under py3 (RhBug:1076884) (Jan Silhan)
- remove: base.deselectGroup(). it is not used. (Ales Kozumplik)
- tests: fix broken InstallMultilib.test_install_src_fails(). (Ales Kozumplik)
- groups: support manipulation with environments (RhBug:1063666) (Ales Kozumplik)
- add dnf.util.partition(). (Ales Kozumplik)
- refactor: RepoPersistor: use the global logger instead of an instance variable. (Ales Kozumplik)
- groups: besides installed groups also store persistently the environments. (Ales Kozumplik)
- rename: persistor.Groups -> ClonableDict. (Ales Kozumplik)
- doc: cli_vs_yum: typography in bandwidth limiting section. (Ales Kozumplik)
- doc: cli_vs_yum: we do not partially allow operations that install .srpm. (RhBug:1080489) (Ales Kozumplik)
- refactor: imports order in cli/commands/__init__.py. (Ales Kozumplik)
- refactor: groups: make all commands use _patterns2groups(). (Ales Kozumplik)
- kernel: remove kernel-source from const.INSTALLONLYPKGS. (Ales Kozumplik)
- build: 0.4.19-1 (Ales Kozumplik)
- New version: 0.4.19 (Ales Kozumplik)
- downloads: bump number of downloaded files on a skip. (RhBug:1079621) (Ales Kozumplik)
- packaging: add dnf.cli.commands to the installation. (Ales Kozumplik)
- refactor: put GroupCommand into its separate module. (Ales Kozumplik)
- rename: make cli.commands a subpackage. (Ales Kozumplik)
- AUTHORS: added Albert. (Ales Kozumplik)
- test: fixed CacheTest.test_noroot() when running as root (Albert Uchytil)
- AUTHORS: added Tim. (Ales Kozumplik)
- fixes TypeError: '_DownloadErrors' object is not iterable (RhBug:1078832) (Tim Lauridsen)
- fixed not including .mo files (Jan Silhan)
- comps: _by_pattern() no longer does the comma splitting. (Ales Kozumplik)

* Mon Mar 24 2014 Aleš Kozumplík <ales@redhat.com> - 0.4.19-1
- downloads: bump number of downloaded files on a skip. (RhBug:1079621) (Ales Kozumplik)
- packaging: add dnf.cli.commands to the installation. (Ales Kozumplik)
- refactor: put GroupCommand into its separate module. (Ales Kozumplik)
- rename: make cli.commands a subpackage. (Ales Kozumplik)
- AUTHORS: added Albert. (Ales Kozumplik)
- test: fixed CacheTest.test_noroot() when running as root (Albert Uchytil)
- AUTHORS: added Tim. (Ales Kozumplik)
- fixes TypeError: '_DownloadErrors' object is not iterable (RhBug:1078832) (Tim Lauridsen)
- fixed not including .mo files (Jan Silhan)
- comps: _by_pattern() no longer does the comma splitting. (Ales Kozumplik)
- including .mo files correctly (Jan Silhan)
- tests: fix locale independence. (Radek Holy)
- remove: unused trashy methods in dnf.yum.misc. (Ales Kozumplik)
- persistor: do not save Groups if it didn't change (RhBug:1077173) (Ales Kozumplik)
- tests: simplify the traceback logging. (Ales Kozumplik)
- main: log IO errors etc. thrown even during Base.__exit__. (Ales Kozumplik)
- logging: do not log IOError tracebacks in verbose mode. (Ales Kozumplik)
- refactor: move out main._main()'s inner error handlers. (Ales Kozumplik)
- added gettext as a build dependency  for translation files (Jan Silhan)
- translation: updated .pot file and fetched fresh .po files from transifex (Jan Silhan)
- removed redundant word from persistor translation (Jan Silhan)
- translation: show relative path in generated pot file (Jan Silhan)
- refactor: replaced type comparisons with isinstance (Jan Silhan)
- translation: added mo files generation and including them in rpm package (Jan Silhan)
- removed unused imports in base.py (Jan Silhan)
- doc: typo in Base.group_install(). (Ales Kozumplik)

* Mon Mar 17 2014 Aleš Kozumplík <ales@redhat.com> - 0.4.18-1
- api: drop items deprecated since 0.4.9 or earlier. (Ales Kozumplik)
- api: deprecate Base.select_group() (Ales Kozumplik)
- doc: document the group marking operations. (Ales Kozumplik)
- api: add Base.group_install() with exclude capability. (Ales Kozumplik)
- groups: recognize 'mark install' instead of 'mark-install'. (Ales Kozumplik)
- Allow installing optional packages from a group. (RhBug:1067136) (Ales Kozumplik)
- groups: add installing groups the object marking style. (Ales Kozumplik)
- groups: add Base.group_remove(). (Ales Kozumplik)
- groups: add support for marking/unmarking groups. (Ales Kozumplik)
- groups: add dnf.persistor.GroupPersistor(), to store the installed groups. (Ales Kozumplik)
- logging: log plugin import tracebacks on the subdebug level. (Ales Kozumplik)
- rename: dnf.persistor.Persistor -> RepoPersistor. (Ales Kozumplik)
- doc: update README and FAQ with the unabbreviated name. (Ales Kozumplik)
- groups: fix grouplist crashes with new libcomps. (Ales Kozumplik)
- Do not terminate for unreadable repository config. (RhBug:1071212) (Ales Kozumplik)
- cli: get rid of ridiculous slashes and the file:// scheme on config read fails. (Ales Kozumplik)
- repo: log more than nothing about a remote repo MD download. (Ales Kozumplik)
- drpm: fallback to .rpm download on drpm rebuild error. (RhBug:1071501) (Ales Kozumplik)
- remove: Base.download_packages()' inner function mediasort(). (Ales Kozumplik)
- tests: tidy up the imports, in particular import mock from support. (Ales Kozumplik)
- changed documentation of distro-sync command (Jan Silhan)
- added distro-sync explicit packages support (RhBug:963710) (Jan Silhan)
- renamed testcase to distro_sync_all (Jan Silhan)
- Minor spelling (Arjun Temurnikar)
- i18n: translate repo sync error message. (Ales Kozumplik)
- add support for ppc64le (Dennis Gilmore)
- there is no arch called arm64 it is aarch64 (Dennis Gilmore)

* Wed Mar 5 2014 Aleš Kozumplík <ales@redhat.com> - 0.4.17-1
- doc: in the faq, warn users who might install rawhide packages on stable. (RhBug:1071677) (Ales Kozumplik)
- cli: better format the download errors report. (Ales Kozumplik)
- drpm: properly report applydeltarpm errors. (RhBug:1071501) (Ales Kozumplik)
- fixed Japanese translatated message (RhBug:1071455) (Jan Silhan)
- generated and synchronized translations with transifex (Jan Silhan)
- added transifex support to cmake (gettext-export, gettext-update) (Jan Silhan)
- api: expose RepoDict.get_matching() and RepoDict.all() (RhBug:1071323) (Ales Kozumplik)
- api: add Repo.set_progress_bar() to the API. (Ales Kozumplik)
- tests: test_cli_progress uses StringIO to check the output. (Ales Kozumplik)
- downloads: fix counting past 100% on mirror failures (RhBug:1070598) (Ales Kozumplik)
- repo: log callback calls to librepo. (Ales Kozumplik)
- Add repository-packages remove-or-reinstall command. (Radek Holy)
- Support negative filtering by new repository name in Base.reinstall. (Radek Holy)
- Support removal N/A packages in Base.reinstall. (Radek Holy)
- Add repository-packages remove command. (Radek Holy)
- refactor: Reduce amount of code in repository-packages subcommands. (Radek Holy)
- Support filtering by repository name in Base.remove. (Radek Holy)
- remove: BaseCli.erasePkgs (Radek Holy)
- Add repository-packages reinstall command. (Radek Holy)
- exceptions: improve empty key handling in DownloadError.__str__(). (Ales Kozumplik)
- downloads: fix fatal error message return value from download_payloads() (RhBug:1071518) (Ales Kozumplik)
- fixes problem with TypeError in Base.read_comps() in python3 (RhBug:1070710) (Tim Lauridsen)
- fix read_comps: not throwing exceptions when repo has no repodata (RhBug:1059704) (Jan Silhan)
- not decompressing groups when --cacheonly option is set (RhBug:1058224) (Jan Silhan)
- added forgotten import (Jan Silhan)
- Add repository-packages move-to command. (Radek Holy)
- Add repository-packages reinstall-old command. (Radek Holy)
- Support filtering by repository name in Base.reinstall. (Radek Holy)
- tests: test effects instead of mock calls. (Radek Holy)
- Wrap some recently added long lines. (Radek Holy)
- remove: BaseCli.reinstallPkgs (Radek Holy)
- repos: repos can never expire. (RhBug:1069538) (Ales Kozumplik)
- build: rebuild with 9d95442 (updated summaries_cache). (Ales Kozumplik)
- doc: update summaries_cache. (Ales Kozumplik)

* Wed Feb 26 2014 Aleš Kozumplík <ales@redhat.com> - 0.4.16-1
- fix: ensure MDPayload always has a valid progress attribute. (RhBug:1069996) (Ales Kozumplik)
- refactor: Move repo-pkgs upgrade-to to a standalone class instead of reusing the UpgradeToCommand. (Radek Holy)
- remove: BaseCli.updatePkgs (Radek Holy)
- refactor: Remove the reference to updatePkgs from UpgradeSubCommand. (Radek Holy)
- refactor: Remove the reference to updatePkgs from UpgradeCommand. (Radek Holy)
- refactor: Move repo-pkgs upgrade to a standalone class instead of reusing the UpgradeCommand. (Radek Holy)
- remove: BaseCli.installPkgs (Radek Holy)
- refactor: Remove the reference to installPkgs from InstallSubCommand. (Radek Holy)
- refactor: Remove the reference to installPkgs from InstallCommand. (Radek Holy)
- refactor: Move repo-pkgs install to a standalone class instead of reusing the InstallCommand. (Radek Holy)
- Revert "Support filtering by repository name in install_groupie." (Radek Holy)
- Revert "Support filtering by repository name in Base.select_group." (Radek Holy)
- Drop group filtering by repository name from installPkgs. (Radek Holy)
- Drop "repo-pkgs install @Group" support. (Radek Holy)
- refactor: Move CheckUpdateCommand.check_updates to BaseCli. (Radek Holy)
- refactor: Move repo-pkgs check-update to a standalone class instead of reusing the CheckUpdateCommand. (Radek Holy)
- refactor: Move repo-pkgs list to a standalone class instead of reusing the ListCommand. (Radek Holy)
- tests: Add tests of repo-pkgs info against the documentation. (Radek Holy)
- Fix "repo-pkgs info installed" behavior with respect to the documentation. (Radek Holy)
- refactor: Move MockBase methods to BaseStubMixin. (Radek Holy)
- refactor: Move repo-pkgs info to a standalone class instead of reusing the InfoCommand. (Radek Holy)
- refactor: Move InfoCommand._print_packages to BaseCli.output_packages. (Radek Holy)
