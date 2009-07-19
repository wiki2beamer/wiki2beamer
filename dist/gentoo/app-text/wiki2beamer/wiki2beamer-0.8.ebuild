# Copyright 1999-2009 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: $

DESCRIPTION="Tool to produce LaTeX Beamer code from wiki-like input."

HOMEPAGE="http://wiki2beamer.sourceforge.net/"
SRC_URI="mirror://sourceforge/${PN}/${P}.zip"

LICENSE="GPL-2 GPL-3"
SLOT="0"
KEYWORDS="~amd64 ~x86"
IUSE=""

DEPEND=""
RDEPEND=">=dev-lang/python-2.4"

src_install() {
	insinto /usr/share/${PF}/examples
	doins doc/examples/*  || die "doins failed"

	doman doc/man/wiki2beamer.1 || die "doman failed"
	dodoc ChangeLog README || die "dodoc failed"
	dobin code/wiki2beamer || die "dobin failed"
}
