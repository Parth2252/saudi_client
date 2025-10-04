/** @odoo-module **/

import {registry} from '@web/core/registry';
import {session} from '@web/session';
import { rpc } from "@web/core/network/rpc";
import {browser} from '@web/core/browser/browser';
import { user } from "@web/core/user";

const mailsendService = {
    dependencies: ['orm', 'action'],
    start(env, {orm, action}) {
        async function getType() {
            return Object.assign({}, {1: {'id': 1,'name': "by_user"}, 2: {'id': 2,'name': "by_company"}});
        }
        async function getSelectedType() {
            var get_user = await orm.searchRead(
                'res.users', [['id','=',user.userId]],
                [
                    'is_mail_by_company',
                ]
            )
            var message = ""
            if (get_user[0].is_mail_by_company==true){
                message = "By Company"
            }
            else{
                message = "By User"
            }
            return await message
        }

        async function setType(type) {
            await orm.write('res.users', [user.userId], {
                is_mail_by_company: type,
            });
            action.doAction('reload_context')
        }
        return {
            getSelectedType,
            getType,
            setType,
        }
    }
};

registry.category('services').add('mailsend', mailsendService);
