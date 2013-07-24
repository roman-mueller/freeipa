# Authors:
#   Petr Vobornik <pvoborni@redhat.com>
#
# Copyright (C) 2013  Red Hat
# see file 'COPYING' for use and warranty information
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
User tests
"""

from ipatests.test_webui.ui_driver import UI_driver
import ipatests.test_webui.data_user as user
import ipatests.test_webui.data_group as group
import ipatests.test_webui.data_netgroup as netgroup
import ipatests.test_webui.data_hbac as hbac
import ipatests.test_webui.test_rbac as rbac
import ipatests.test_webui.data_sudo as sudo


class test_user(UI_driver):

    def test_crud(self):
        """
        Basic CRUD: user
        """
        self.init_app()
        self.basic_crud(user.ENTITY, user.DATA)

    def test_associations(self):
        """
        User direct associations
        """

        self.init_app()

        # prepare - add user, group, netgroup, role, hbac rule, sudo rule
        # ---------------------------------------------------------------
        self.add_record(user.ENTITY, user.DATA, navigate=False)
        self.add_record(group.ENTITY, group.DATA)
        self.add_record(netgroup.ENTITY, netgroup.DATA)
        self.add_record(rbac.ROLE_ENTITY, rbac.ROLE_DATA)
        self.add_record(hbac.RULE_ENTITY, hbac.RULE_DATA)
        self.add_record(sudo.RULE_ENTITY, sudo.RULE_DATA)

        # add & remove associations
        # -------------------------
        self.navigate_to_entity(user.ENTITY)
        self.navigate_to_record(user.PKEY)

        self.add_associations([group.PKEY, 'editors'], facet='memberof_group', delete=True)
        self.add_associations([netgroup.PKEY], facet='memberof_netgroup', delete=True)
        self.add_associations([rbac.ROLE_PKEY], facet='memberof_role', delete=True)
        self.add_associations([hbac.RULE_PKEY], facet='memberof_hbacrule', delete=True)
        self.add_associations([sudo.RULE_PKEY], facet='memberof_sudorule', delete=True)

        # cleanup
        # -------
        self.delete(user.ENTITY, [user.DATA])
        self.delete(group.ENTITY, [group.DATA])
        self.delete(netgroup.ENTITY, [netgroup.DATA])
        self.delete(rbac.ROLE_ENTITY, [rbac.ROLE_DATA])
        self.delete(hbac.RULE_ENTITY, [hbac.RULE_DATA])
        self.delete(sudo.RULE_ENTITY, [sudo.RULE_DATA])

    def test_indirect_associations(self):
        """
        User indirect associations
        """
        self.init_app()

        # add
        # ---
        self.add_record(user.ENTITY, user.DATA, navigate=False)

        self.add_record(group.ENTITY, group.DATA)
        self.navigate_to_record(group.PKEY)
        self.add_associations([user.PKEY])

        self.add_record(group.ENTITY, group.DATA2)
        self.navigate_to_record(group.PKEY2)
        self.add_associations([group.PKEY], facet='member_group')

        self.add_record(netgroup.ENTITY, netgroup.DATA)
        self.navigate_to_record(netgroup.PKEY)
        self.add_table_associations('memberuser_group', [group.PKEY2])

        self.add_record(rbac.ROLE_ENTITY, rbac.ROLE_DATA)
        self.navigate_to_record(rbac.ROLE_PKEY)
        self.add_associations([group.PKEY2], facet='member_group')

        self.add_record(hbac.RULE_ENTITY, hbac.RULE_DATA)
        self.navigate_to_record(hbac.RULE_PKEY)
        self.add_table_associations('memberuser_group', [group.PKEY2])

        self.add_record(sudo.RULE_ENTITY, sudo.RULE_DATA)
        self.navigate_to_record(sudo.RULE_PKEY)
        self.add_table_associations('memberuser_group', [group.PKEY2])

        # check indirect associations
        # ---------------------------
        self.navigate_to_entity(user.ENTITY, 'search')
        self.navigate_to_record(user.PKEY)

        self.assert_indirect_record(group.PKEY2, user.ENTITY, 'memberof_group')
        self.assert_indirect_record(netgroup.PKEY, user.ENTITY, 'memberof_netgroup')
        self.assert_indirect_record(rbac.ROLE_PKEY, user.ENTITY, 'memberof_role')
        self.assert_indirect_record(hbac.RULE_PKEY, user.ENTITY, 'memberof_hbacrule')
        self.assert_indirect_record(sudo.RULE_PKEY, user.ENTITY, 'memberof_sudorule')

        ## cleanup
        ## -------
        self.delete(user.ENTITY, [user.DATA])
        self.delete(group.ENTITY, [group.DATA, group.DATA2])
        self.delete(netgroup.ENTITY, [netgroup.DATA])
        self.delete(rbac.ROLE_ENTITY, [rbac.ROLE_DATA])
        self.delete(hbac.RULE_ENTITY, [hbac.RULE_DATA])
        self.delete(sudo.RULE_ENTITY, [sudo.RULE_DATA])

    def test_actions(self):
        """
        Test user actions
        """
        self.init_app()

        self.add_record(user.ENTITY, user.DATA, navigate=False)
        self.navigate_to_record(user.PKEY)

        self.disable_action()
        self.enable_action()

        # reset password
        pwd = self.config.get('ipa_password')
        fields = [
            ('password', 'password1', pwd),
            ('password', 'password2', pwd),
        ]
        self.action_panel_action('account_actions', 'reset_password')
        self.assert_dialog()
        self.fill_fields(fields)
        self.dialog_button_click('reset_password')
        self.wait_for_request(n=2)
        self.assert_no_error_dialog()
        self.assert_text_field('has_password', '******')

        # delete
        self.delete_action(user.ENTITY, user.PKEY)
