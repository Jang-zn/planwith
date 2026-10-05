import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'skill/scripts'))
import doctor
import peer
import report
from rounds import manage


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False), encoding='utf-8')


def fixture(root, topic='001-target'):
    records=root/'records'
    folder=records/'discussions'/topic
    write(folder/'state.json', {'status':'finished', 'rubric':'general'})
    (folder/'discussion.md').write_text('Fixture judge: available evidence only.', encoding='utf-8')
    write(records/'evidence.json', [{'id':'E-01','kind':'hypothesis','claim':'Needs testing','source':'Fixture brief','checked_at':'2026-01-01','limitation':'Not observed'}])
    scores=[{'value':None,'reason':'Insufficient evidence','evidence':[],'limitation':'No study','revisit':'Interview'} for _ in range(5)]
    data={'id':topic,'title':'Target','status':'finished','recommendation':'Validate first <script>alert(1)</script>', 'confidence':'Low','approval':'pending','approval_evidence':[], 'rubric':'general', 'questions':[], 'unknowns':['Interview needed'],'blockers':[],'dissent':'Unresolved','next_action':'Interview','alternatives':[{'name':'Option A','scores':scores}]}
    write(folder/'conclusion.json', data)
    write(records/'report.json', {'title':'Fixture report','summary':'A test, not a real plan','topic_ids':[topic]})
    write(records/'impacts.json', [])
    return folder, data


class ReportTests(unittest.TestCase):
    def test_render_escape_null_and_integrity(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp).resolve(); folder, _=fixture(root)
            output=report.render(root)
            contents=output.read_text(encoding='utf-8')
            self.assertNotIn('<script>alert',contents)
            self.assertIn('&lt;script&gt;', contents)
            self.assertIn('총점 미산출', contents)
            self.assertTrue(report.verify(root))
            output.write_text(contents.replace('Target','Tampered'),encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'content changed'):
                report.verify(root)
            report.render(root)
            (folder/'discussion.md').write_text('New evidence',encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'stale'):
                report.verify(root)

    def test_missing_topic_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp).resolve(); fixture(root)
            write(root/'records/report.json',{'title':'T','summary':'S','topic_ids':[]})
            with self.assertRaisesRegex(ValueError,'omit'):
                report.render(root)

    def test_approval_rubric_and_scores(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp).resolve(); folder,data=fixture(root)
            for change, message in [({'approval':'approved'},'approval needs'), ({'rubric':'design'},'Rubric differs'), ({'status':'active'},'status differs')]:
                write(folder/'conclusion.json',dict(data,**change))
                with self.assertRaisesRegex(ValueError,message):
                    report.render(root)
            data['alternatives'][0]['scores'][0]['value']=6
            write(folder/'conclusion.json',data)
            with self.assertRaisesRegex(ValueError,'0–5'):
                report.render(root)

    def test_numeric_scores_require_known_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp).resolve();folder,data=fixture(root)
            score=data['alternatives'][0]['scores'][0]
            score['value']=3
            write(folder/'conclusion.json',data)
            with self.assertRaisesRegex(ValueError,'needs evidence'):
                report.render(root)
            score['evidence']=['NO-SUCH-ID']
            write(folder/'conclusion.json',data)
            with self.assertRaisesRegex(ValueError,'Unknown score'):
                report.render(root)


class DoctorTests(unittest.TestCase):
    def test_overrides_do_not_leak_values(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ,{'OPENAI_API_KEY':'SECRET_NEVER_PRINT'},clear=True), patch.object(doctor.shutil,'which',return_value=None):
            result=doctor.inspect(tmp)
            self.assertFalse(result['ok'])
            self.assertNotIn('SECRET_NEVER_PRINT',json.dumps(result))
            self.assertIn('OPENAI_API_KEY',json.dumps(result))


class WorkflowTests(unittest.TestCase):
    def test_both_host_directions_input_gate_and_next_round(self):
        for host,other in [('codex','claude'),('claude','codex')]:
            with self.subTest(host=host), tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ,{},clear=True):
                root=Path(tmp).resolve()
                first=manage(root,'docs','new','Fixture initial idea',mode='quick')
                topic=first/'records/discussions/001-target'
                base=['peer.py','--project',tmp,'--topic',str(topic.relative_to(root))]
                def invoke(*args):
                    with patch.object(sys,'argv',base+list(args)):
                        peer.main()
                invoke('init','--title','Target')
                invoke('pause','--question','Fixture: personal or commercial?')
                prompt=root/'prompt.txt';prompt.write_text('Fixture prompt',encoding='utf-8')
                with self.assertRaisesRegex(ValueError,'not active'):
                    invoke('call','--provider',other,'--phase','proposal','--prompt-file',str(prompt))
                reply=root/'reply.txt';reply.write_text('Fixture user answer: personal.',encoding='utf-8')
                invoke('answer','--file',str(reply))
                auth_output='Logged in using ChatGPT' if other=='codex' else '{"loggedIn":true,"authMethod":"claude.ai"}'
                auth=subprocess.CompletedProcess([],0,auth_output,'')
                with patch.object(peer.shutil,'which',return_value=other),patch.object(peer.subprocess,'run',return_value=auth),patch.object(peer,'run',return_value='Fixture contribution: pending real evidence.') as runner:
                    for phase in ('proposal','critique','revision','judge'):
                        invoke('call','--provider',other,'--phase',phase,'--prompt-file',str(prompt))
                    self.assertEqual(runner.call_count,4)
                    self.assertTrue(all(call.args[0][0]==other for call in runner.call_args_list))
                invoke('finish','--reason','Fixture completed')
                state=json.loads((topic/'state.json').read_text(encoding='utf-8'))
                transcript=(topic/'discussion.md').read_text(encoding='utf-8')
                fixture(first)
                write(topic/'state.json',state)
                (topic/'discussion.md').write_text(transcript,encoding='utf-8')
                output=report.render(first)
                self.assertTrue(report.verify(first))
                original=hashlib.sha256(output.read_bytes()).hexdigest()
                manage(root,'docs','close')
                second=manage(root,'docs','new','Fixture user requested narrower scope')
                fixture(second)
                write(second/'records/impacts.json',[{'decision':'Scope','before':'Broad','after':'Narrow','reason':'Fixture feedback','areas':[{'name':'MVP','status':'updated','reason':'Removed one feature'},{'name':'Pricing','status':'review_needed','reason':'Demand unknown'}]}])
                report.render(second)
                self.assertTrue(report.verify(second))
                self.assertEqual(hashlib.sha256(output.read_bytes()).hexdigest(),original)
                self.assertIn('User answer',transcript)

    def test_recovery_keeps_budget(self):
        state={'status':'active','calls':[{'status':'failed'}],'elapsed_seconds':30}
        details=peer.recovery(state)
        self.assertEqual(details['calls_remaining'],7)
        self.assertIn('did not complete',details['next_action'])
        state['status']='waiting_for_user'
        self.assertIn('actual user answer',peer.recovery(state)['next_action'])
