#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    : local_hunter.py
@Desc    : 本地文件敏感信息扫描
@Author  : thinksec
@Date    : 2022/9/8
"""
import argparse
import datetime
import os
import re
from typing import Sequence, Optional

from concurrent.futures import ProcessPoolExecutor, as_completed
from rich import print
from rich.progress import track

from .config import black_dir, black_filename, black_suffix, rules
from .util import check_target_in_black_list


class LocalHunter(object):
    def __init__(self, filenames, proj_name=None, report_file=None, mail_to=None):
        self.rules = rules  # 初始化规则
        self.filenames = filenames
        self.report_file = report_file
        self.proj_name = proj_name if proj_name else "HunterInfo"
        self.mail_to = mail_to
        self.all_file_res = []
        self.scan_file_list = []
        self.html_report_content = ""

    def generate_html_report(self):
        file_content = "<html><body>漏洞详情:<br>"
        for res in self.all_file_res:
            tb_content = ""
            for key, value in res['data'].items():
                line_c = ""
                for line in value:
                    line_c = line_c + f"<p>{line}</p>"
                tb_content = tb_content + f"""
                        <tr>
                            <td width="10%" nowrap="nowrap">{key}</td>
                            <td width="90%">{line_c}</td>
                        </tr>                
                    """
            file_content = file_content + f"""
                    <a href='file:///{os.path.join(os.getcwd(), res['filepath'])}' target='_blank' type='text/plain' >
                        <h5>{res['filepath']}</h5>
                    </a>
                    <table border="1" cellspacing="0" width="100%">
                        <th>规则</th><th>敏感信息</th>
                        {tb_content}
                    </table>
                """
        end_content = """
            <p>
            修复建议：<br>
                一、敏感信息修复指引：<br>
                    1、将暴露的ip换成127.0.0.1、localhost或者192.168.1.1等非敏感ip。<br>
                    2、内部域名应使用localhost或者其他公网非敏感域名webank.com等代替。<br>
                    3、配置文件中账号密码修改为default、password等通用密码标记或置空<br>
                    4. 其他类敏感信息请根据KM详细修复指引排查处理。<br>
                    <br>
                二、如果确认为误报导致无法提交，可以通过以下方式跳过检查进行提交<br>
                    git commit -m "update" --no-verify <br> 
                    <br>
                如有疑问请联系thinksec，谢谢<br>
            </p>

        </body>
        </html>
            """
        self.html_report_content = file_content + end_content

    def save_local_report(self):
        if not self.report_file:
            time_stamp = datetime.datetime.now()
            now_time = time_stamp.strftime('%Y_%m_%d_%H_%M_%S')
            self.report_file = f"{self.proj_name}-{now_time}.html"
        report_dir = os.path.join(os.path.expanduser('~'), 'hunter-info')
        if not os.path.exists(report_dir):
            os.mkdir(report_dir)
        save_local_path = os.path.join(report_dir, self.report_file)
        with open(save_local_path, 'w+') as f:
            f.write(self.html_report_content)
        print(f"Please check the scan report in path: {save_local_path}")

    def scan_file(self, filename):
        # print(filename)
        file_res = {"filepath": filename, "data": {}}
        try:
            with open(filename, 'r+', encoding='utf-8') as f:
                contents = f.read()
        except Exception as e:
            return file_res
        i = 0
        contents_len = len(contents)
        if contents_len > 1000000:  # 文件大于1M, 跳过
            # print(f"文件: {filename}过大, 跳过...")
            return file_res
        while i < contents_len:
            for ruleItem in self.rules:
                # 文件太大被卡死，每次取10000分割出来扫描
                res = re.compile(ruleItem['rule'], flags=re.IGNORECASE).findall(contents[i:i + 10000])
                new_res = []
                for res_item in res:
                    if isinstance(res_item, tuple):
                        res_item = res_item[0]
                    if not check_target_in_black_list(target=res_item, black_list=ruleItem['black']):
                        new_res.append(res_item)
                        if ruleItem['desc'] in file_res["data"]:  # 合并该规则的扫描结果
                            new_res = new_res + file_res["data"].get(ruleItem['desc'])
                        file_res["data"].update({
                            ruleItem['desc']: list(set(new_res))
                        })
            i = i + 10000
        return file_res

    def do_scan(self):
        # print(self.filenames)
        for filename in self.filenames:
            suffix = os.path.splitext(filename)[1]
            if suffix in black_suffix:  # 文件后缀黑名单
                continue
            if filename in black_filename:  # 文件名黑名单
                continue
            self.scan_file_list.append(filename)

        job_results = []
        with ProcessPoolExecutor() as executor:
            jobs = []
            for i in self.scan_file_list:
                jobs.append(executor.submit(self.scan_file, i))
            for job in track(as_completed(jobs), total=len(self.scan_file_list), description="running:"):
                # print(job.result())
                job_results.append(job.result())
        for file_res in job_results:
            if file_res.get("data"):
                self.all_file_res.append(file_res)
        if self.all_file_res:
            self.generate_html_report()
            self.save_local_report()

        return len(self.all_file_res)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('filenames', nargs='*', help='Filenames to scan')
    args = parser.parse_args(argv)
    hunter = LocalHunter(args.filenames)
    return_code = hunter.do_scan()
    print(f"{return_code} sensitive information found. can't commit!")
    return return_code


if __name__ == '__main__':
    raise SystemExit(main())
