# -*- encoding: utf-8 -*-
from openerp import http
from openerp.http import request

import logging

_logger = logging.getLogger(__name__)


class RunbotController(http.Controller):
    @http.route('/runbot/webhook/push',
                type='json', auth="none")
    def push_event(self, req):
        env = request.env
        json_dict = req.jsonrequest
        token = req.httprequest.args.get('token')
        # Read information sent from webhook
        ref = json_dict['ref']
        repo = json_dict['repository']['url']
        commit = json_dict['commits'][0]
        # Verify token before continue
        repository = env['runbot.repo'].sudo().search([
            ('name', '=', repo), ('token', '=', token)], limit=1)
        if not repository:
            _logger.info('Received wrong token for repo: %s' % repo)
            return
        build = env['runbot.build'].sudo().search([
            ('repo_id.id', '=', repository.id),
            ('branch_id.ref_name', '=', ref),
            ('commit', '=', commit['id'])], limit=1)
        if not build:
            branch = env['runbot.branch'].sudo().search([
                ('ref_name', '=', ref),
                ('repo_id', '=', repository and repository.id)], limit=1)
            env['runbot.build'].sudo().create({
                'commit': commit['id'],
                'branch_id': branch.id,
            })
        else:
            env['runbot.build'].sudo().schedule(build.id)
