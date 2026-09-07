#!/usr/bin/env python3
"""Complete and verify the Monad Engineering Program GitHub Project.

This script mutates only the GitHub Project coordination projection. Canonical
Git/EOS artifacts remain authoritative.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from typing import Any

API_VERSION = "2026-03-10"

ITEM_TYPE_OPTIONS = (
    "Initiative", "Epic", "Feature", "Story", "Enabler", "Task",
    "Work Packet", "Bug", "Defect", "Change Request",
)
LIFECYCLE_OPTIONS = (
    "Backlog", "Refining", "Ready", "Authorized", "Running",
    "Review", "Verified", "Closed", "Blocked",
)
OPTION_COLORS = {
    "Initiative":"PURPLE", "Epic":"PURPLE", "Feature":"BLUE",
    "Story":"GREEN", "Enabler":"YELLOW", "Task":"GRAY",
    "Work Packet":"GREEN", "Bug":"RED", "Defect":"RED",
    "Change Request":"ORANGE", "Backlog":"GRAY", "Refining":"YELLOW",
    "Ready":"BLUE", "Authorized":"PURPLE", "Running":"GREEN",
    "Review":"YELLOW", "Verified":"BLUE", "Closed":"GRAY", "Blocked":"RED",
}
OPTION_DESCRIPTIONS = {
    "Initiative":"Finite outcome-oriented program grouping beneath a Product Goal",
    "Epic":"Major capability or outcome within an Initiative",
    "Feature":"Feature-sized product or engineering outcome",
    "Story":"User/system outcome within a Feature",
    "Enabler":"Technical or architectural work enabling product outcomes",
    "Task":"Concrete refined unit of implementation work",
    "Work Packet":"Governed executable realization of planned work",
    "Bug":"Product defect", "Defect":"Engineering-system or control-plane defect",
    "Change Request":"Governed request to change accepted scope or behavior",
    "Backlog":"Planned but not yet Ready", "Refining":"Being refined toward readiness",
    "Ready":"Ready but not necessarily Authorized", "Authorized":"Explicitly authorized for execution",
    "Running":"Execution is in progress", "Review":"Awaiting review",
    "Verified":"Verification evidence accepted", "Closed":"Completed/closed",
    "Blocked":"Unable to proceed",
}

REQUIRED_VIEWS: tuple[dict[str, Any], ...] = (
    {
        "name":"Program", "layout":"table", "filter":'is:issue label:"type:initiative"',
        "visible":("Title","Product Goal","Initiative","Lifecycle","Priority","Target Release"),
        "group_by":("Product Goal",), "sort_by":(("Initiative","asc"),),
    },
    {
        "name":"MVP Roadmap", "layout":"roadmap",
        "filter":'is:issue label:"release:mvp-1" label:"type:initiative","type:epic","type:feature"',
        "group_by":("Initiative",), "sort_by":(("Epic","asc"),("Feature","asc")),
    },
    {
        "name":"Current Work", "layout":"board",
        "filter":"is:issue lifecycle:Ready,Authorized,Running,Review,Blocked",
        "visible":("Title","Item Type","Initiative","Epic","Feature","Work Cycle","Work Packet","Priority"),
        "vertical_group_by":("Lifecycle",),
    },
    {
        "name":"Next Up", "layout":"table", "filter":"is:issue lifecycle:Ready",
        "visible":("Title","Item Type","Initiative","Epic","Feature","Work Cycle","Work Packet","Priority","Risk"),
        "group_by":("Initiative",), "sort_by":(("Priority","asc"),("Work Cycle","asc")),
    },
    {
        "name":"Defects", "layout":"board", "filter":'is:issue label:"type:defect","type:bug"',
        "visible":("Title","Lifecycle","Priority","Risk","Product Area","Domain"),
        "vertical_group_by":("Lifecycle",),
    },
    {
        "name":"Release 1", "layout":"table", "filter":'is:issue label:"release:mvp-1"',
        "visible":("Title","Item Type","Initiative","Epic","Feature","Lifecycle","Priority","Work Cycle","Work Packet"),
        "group_by":("Initiative",), "sort_by":(("Epic","asc"),("Feature","asc")),
    },
    {
        "name":"Work Cycles", "layout":"table", "filter":"is:issue",
        "visible":("Title","Item Type","Initiative","Epic","Feature","Work Cycle","Work Packet","Lifecycle","Priority"),
        "group_by":("Work Cycle",), "sort_by":(("Work Cycle","asc"),("Priority","asc")),
    },
    {
        "name":"By Initiative", "layout":"table", "filter":"is:issue",
        "visible":("Title","Item Type","Initiative","Epic","Feature","Lifecycle","Priority","Work Cycle"),
        "group_by":("Initiative",), "sort_by":(("Epic","asc"),("Feature","asc")),
    },
    {
        "name":"By Epic", "layout":"table", "filter":"is:issue",
        "visible":("Title","Item Type","Initiative","Epic","Feature","Lifecycle","Priority","Work Cycle"),
        "group_by":("Epic",), "sort_by":(("Feature","asc"),("Priority","asc")),
    },
    {
        "name":"By Feature", "layout":"table", "filter":"is:issue",
        "visible":("Title","Item Type","Initiative","Epic","Feature","Lifecycle","Priority","Work Cycle","Work Packet"),
        "group_by":("Feature",), "sort_by":(("Priority","asc"),),
    },
    {
        "name":"Work Packets", "layout":"table", "filter":'is:issue label:"type:work-packet"',
        "visible":("Title","Initiative","Epic","Feature","Increment","Work Cycle","Work Packet","Lifecycle","Priority"),
        "group_by":("Work Cycle",), "sort_by":(("Work Cycle","asc"),("Priority","asc")),
    },
    {
        "name":"Product Backlog", "layout":"table", "filter":'is:issue label:"release:mvp-1" -lifecycle:Closed',
        "visible":("Title","Item Type","Initiative","Epic","Feature","Lifecycle","Priority","Work Cycle","Work Packet"),
        "group_by":("Initiative",), "sort_by":(("Priority","asc"),("Work Cycle","asc")),
    },
    {
        "name":"Blocked", "layout":"table", "filter":"is:issue lifecycle:Blocked",
        "visible":("Title","Item Type","Initiative","Epic","Feature","Priority","Risk","Work Cycle","Work Packet"),
        "group_by":("Initiative",), "sort_by":(("Priority","asc"),),
    },
    {
        "name":"Dogfooding", "layout":"table", "filter":'is:issue label:"area:github"',
        "visible":("Title","Item Type","Initiative","Epic","Feature","Lifecycle","Priority","Work Cycle","Work Packet"),
        "group_by":("Epic",), "sort_by":(("Priority","asc"),),
    },
    {
        "name":"AI / Agents", "layout":"table", "filter":'is:issue label:"area:agent","area:execution"',
        "visible":("Title","Item Type","Initiative","Epic","Feature","Lifecycle","Executor","Priority","Work Cycle"),
        "group_by":("Initiative",), "sort_by":(("Epic","asc"),("Priority","asc")),
    },
    {
        "name":"Semantic Core", "layout":"table",
        "filter":'is:issue label:"area:workspace","area:ingestion","area:graph","area:kir","area:diagnostics","area:query"',
        "visible":("Title","Item Type","Initiative","Epic","Feature","Lifecycle","Priority","Work Cycle","Work Packet"),
        "group_by":("Epic",), "sort_by":(("Feature","asc"),("Priority","asc")),
    },
    {
        "name":"Architecture & Specs", "layout":"table", "filter":'is:issue label:"area:governance"',
        "visible":("Title","Item Type","Initiative","Epic","Feature","Lifecycle","ADR","Specification","Priority"),
        "group_by":("Initiative",), "sort_by":(("Epic","asc"),("Priority","asc")),
    },
    {
        "name":"Codex Queue", "layout":"table",
        "filter":"is:issue executor:Codex,Mixed lifecycle:Ready,Authorized,Running",
        "visible":("Title","Executor","Lifecycle","Initiative","Epic","Feature","Work Cycle","Work Packet","Priority","Risk"),
        "group_by":("Lifecycle",), "sort_by":(("Priority","asc"),("Work Cycle","asc")),
    },
    {
        "name":"Release Readiness", "layout":"table", "filter":'is:issue label:"release:mvp-1" label:"area:release"',
        "visible":("Title","Item Type","Initiative","Epic","Feature","Lifecycle","Priority","Risk","Work Cycle","Work Packet"),
        "group_by":("Epic",), "sort_by":(("Priority","asc"),("Work Cycle","asc")),
    },
    {
        "name":"Risks & Decisions", "layout":"table", "filter":"is:issue risk:Critical,High",
        "visible":("Title","Risk","Item Type","Initiative","Epic","Feature","ADR","Specification","Lifecycle","Priority"),
        "group_by":("Initiative",), "sort_by":(("Risk","asc"),("Priority","asc")),
    },
    {
        "name":"Recently Completed", "layout":"table", "filter":"is:issue lifecycle:Verified,Closed updated:>@today-30d",
        "visible":("Title","Item Type","Initiative","Epic","Feature","Lifecycle","Updated"),
        "group_by":("Initiative",), "sort_by":(("Updated","desc"),),
    },
)

REQUIRED_FIELDS = (
    "Item Type","Product Goal","Initiative","Epic","Feature","Priority","Criticality",
    "Product Area","Domain","Increment","Work Cycle","Lifecycle","Story Points","Risk",
    "Executor","Work Packet","Specification","ADR","Target Release","Start Date","Target Date",
)


def run(args:list[str], *, input_text:str|None=None, check:bool=True)->subprocess.CompletedProcess[str]:
    proc=subprocess.run(args,input=input_text,text=True,capture_output=True,check=False)
    if check and proc.returncode!=0:
        detail=proc.stderr.strip() or proc.stdout.strip() or "unknown command error"
        raise RuntimeError(f"{' '.join(args)} failed: {detail}")
    return proc


def gh_json(*args:str)->Any:
    return json.loads(run(["gh",*args]).stdout)


def graphql(query:str, variables:dict[str,Any])->dict[str,Any]:
    payload=json.dumps({"query":query,"variables":variables})
    response=json.loads(run(["gh","api","graphql","--input","-"],input_text=payload).stdout)
    if response.get("errors"):
        raise RuntimeError(f"GitHub GraphQL error: {response['errors']}")
    return response.get("data") or {}


def normalized(value:str|None)->str:
    return re.sub(r"[^a-z0-9]+","",(value or "").casefold())


def project_query(org:str, number:int)->dict[str,Any]:
    data=graphql("""
    query($org:String!,$number:Int!){organization(login:$org){projectV2(number:$number){
      id number title
      fields(first:100){nodes{
        ... on ProjectV2FieldCommon{id name dataType}
        ... on ProjectV2SingleSelectField{id name dataType options{id name color description}}
      }}
      views(first:100){nodes{id number name layout filter}}
    }}}""",{"org":org,"number":number})
    project=(data.get("organization") or {}).get("projectV2")
    if not project:
        raise RuntimeError(f"Could not resolve organization Project {org}#{number}")
    return project


def resolve_field(fields:list[dict[str,Any]], wanted:str, *, allow_legacy_equivalent:bool=True)->dict[str,Any]:
    exact=[f for f in fields if (f.get("name") or "").casefold()==wanted.casefold()]
    if len(exact)==1:
        return exact[0]
    if len(exact)>1:
        raise RuntimeError(f"Ambiguous Project fields for {wanted!r}: {[f.get('name') for f in exact]}")
    if allow_legacy_equivalent:
        eq=[f for f in fields if normalized(f.get("name"))==normalized(wanted)]
        if len(eq)==1:
            return eq[0]
        if len(eq)>1:
            raise RuntimeError(f"Ambiguous Project fields for {wanted!r}: {[f.get('name') for f in eq]}")
    raise RuntimeError(f"Required Project field not found: {wanted}")


def canonicalize_field_names(project:dict[str,Any])->int:
    fields=[f for f in project["fields"]["nodes"] if f]
    changes=0
    for canonical in ("Work Cycle","Work Packet"):
        exact=[f for f in fields if (f.get("name") or "").casefold()==canonical.casefold()]
        if exact:
            continue
        eq=[f for f in fields if normalized(f.get("name"))==normalized(canonical)]
        if len(eq)>1:
            raise RuntimeError(f"Cannot canonicalize {canonical!r}; ambiguous legacy fields: {[f.get('name') for f in eq]}")
        if len(eq)!=1:
            continue
        field=eq[0]
        old=field.get("name") or ""
        graphql("""mutation($fieldId:ID!,$name:String!){updateProjectV2Field(input:{fieldId:$fieldId,name:$name}){projectV2Field{... on ProjectV2FieldCommon{id name}}}}""",{"fieldId":field["id"],"name":canonical})
        print(f"Renamed Project field {old!r} -> {canonical!r}.")
        changes+=1
    return changes


def ensure_single_select_options(project:dict[str,Any], field_name:str, required:tuple[str,...])->int:
    fields=[f for f in project["fields"]["nodes"] if f]
    field=resolve_field(fields,field_name)
    if field.get("dataType")!="SINGLE_SELECT":
        raise RuntimeError(f"Project field {field_name!r} is not SINGLE_SELECT")
    existing=list(field.get("options") or [])
    have={(o.get("name") or "").casefold() for o in existing}
    missing=[name for name in required if name.casefold() not in have]
    if not missing:
        print(f"Project field {field.get('name')!r}: all required options present.")
        return 0
    options=[{"id":o["id"],"name":o["name"],"color":o.get("color") or "GRAY","description":o.get("description") or ""} for o in existing]
    options.extend({"name":name,"color":OPTION_COLORS.get(name,"GRAY"),"description":OPTION_DESCRIPTIONS.get(name,"")} for name in missing)
    graphql("""mutation($fieldId:ID!,$options:[ProjectV2SingleSelectFieldOptionInput!]!){updateProjectV2Field(input:{fieldId:$fieldId,singleSelectOptions:$options}){projectV2Field{... on ProjectV2SingleSelectField{id name}}}}""",{"fieldId":field["id"],"options":options})
    print(f"Project field {field.get('name')!r}: added option(s): {', '.join(missing)}")
    return len(missing)


def rest_fields(org:str, number:int)->list[dict[str,Any]]:
    payload=gh_json("api","-H","Accept: application/vnd.github+json","-H",f"X-GitHub-Api-Version: {API_VERSION}",f"orgs/{org}/projectsV2/{number}/fields?per_page=100")
    if isinstance(payload,list):
        return payload
    if isinstance(payload,dict):
        for key in ("fields","values"):
            if isinstance(payload.get(key),list):
                return payload[key]
    raise RuntimeError("Unexpected Project fields REST response")


def field_database_id(fields:list[dict[str,Any]], wanted:str)->int:
    exact=[f for f in fields if (f.get("name") or "").casefold()==wanted.casefold()]
    if len(exact)==1:
        return int(exact[0]["id"])
    eq=[f for f in fields if normalized(f.get("name"))==normalized(wanted)]
    if len(eq)==1:
        return int(eq[0]["id"])
    matches=exact if len(exact)>1 else eq
    if matches:
        raise RuntimeError(f"Ambiguous REST Project fields for {wanted!r}: {[f.get('name') for f in matches]}")
    raise RuntimeError(f"Required REST Project field not found: {wanted}")


def view_body(spec:dict[str,Any], fields:list[dict[str,Any]])->dict[str,Any]:
    body:dict[str,Any]={"name":spec["name"],"layout":spec["layout"],"filter":spec["filter"]}
    if spec["layout"]!="roadmap":
        body["visible_fields"]=[field_database_id(fields,n) for n in spec.get("visible",())]
    if spec.get("group_by"):
        body["group_by"]=[field_database_id(fields,spec["group_by"][0])]
    if spec.get("vertical_group_by"):
        body["vertical_group_by"]=[field_database_id(fields,spec["vertical_group_by"][0])]
    if spec.get("sort_by"):
        body["sort_by"]=[[field_database_id(fields,n),d] for n,d in spec["sort_by"]]
    return body


def create_view(org:str, number:int, spec:dict[str,Any], fields:list[dict[str,Any]])->None:
    run(["gh","api","--method","POST","-H","Accept: application/vnd.github+json","-H",f"X-GitHub-Api-Version: {API_VERSION}",f"orgs/{org}/projectsV2/{number}/views","--input","-"],input_text=json.dumps(view_body(spec,fields)))


def ensure_views(org:str, number:int)->int:
    project=project_query(org,number)
    existing={(v.get("name") or "").casefold():v for v in project["views"]["nodes"] if v}
    fields=rest_fields(org,number)
    created=0
    for spec in REQUIRED_VIEWS:
        current=existing.get(spec["name"].casefold())
        if current:
            print(f"Project view {spec['name']!r} already exists (#{current.get('number')}).")
            continue
        create_view(org,number,spec,fields)
        created+=1
        print(f"Created Project view: {spec['name']}")
    return created


def normalize_layout(value:str|None)->str:
    return (value or "").casefold().replace("_layout","")


def project_query_count(org:str, number:int, query:str)->int:
    result=gh_json("project","item-list",str(number),"--owner",org,"--limit","1000","--query",query,"--format","json")
    return len(result.get("items",[]))


def verify(org:str, repo:str, number:int)->int:
    failures:list[str]=[]
    warnings:list[str]=[]
    project=project_query(org,number)
    fields=[f for f in project["fields"]["nodes"] if f]

    for field_name in REQUIRED_FIELDS:
        try:
            resolve_field(fields,field_name,allow_legacy_equivalent=False)
        except RuntimeError as exc:
            failures.append(str(exc))

    for field_name,required in (("Item Type",ITEM_TYPE_OPTIONS),("Lifecycle",LIFECYCLE_OPTIONS)):
        try:
            field=resolve_field(fields,field_name)
            have={(o.get("name") or "").casefold() for o in field.get("options") or []}
            missing=[name for name in required if name.casefold() not in have]
            if missing:
                failures.append(f"{field_name} missing option(s): {', '.join(missing)}")
        except RuntimeError as exc:
            failures.append(str(exc))

    views={(v.get("name") or "").casefold():v for v in project["views"]["nodes"] if v}
    for spec in REQUIRED_VIEWS:
        view=views.get(spec["name"].casefold())
        if not view:
            failures.append(f"Required Project view missing: {spec['name']}")
            continue
        if normalize_layout(view.get("layout"))!=spec["layout"]:
            warnings.append(f"View {spec['name']!r} layout is {view.get('layout')!r}; canonical default is {spec['layout']!r}")
        current_filter=(view.get("filter") or "").strip()
        if current_filter and current_filter!=spec["filter"]:
            warnings.append(f"View {spec['name']!r} preserves custom filter {current_filter!r}; canonical default is {spec['filter']!r}")

    total_issues=len(gh_json("issue","list","-R",f"{org}/{repo}","--state","all","--limit","1000","--json","number"))
    total_items=len(gh_json("project","item-list",str(number),"--owner",org,"--limit","1000","--format","json").get("items",[]))
    if total_items<total_issues:
        failures.append(f"Project has {total_items} items but repository has {total_issues} issues")

    checks=(
        ("initiatives",'label:"type:initiative"',1),
        ("MVP Release 1",'label:"release:mvp-1"',1),
        ("Tasks",'"Item Type":Task',1),
        ("Running work","lifecycle:Running",1),
    )
    for label,query,minimum in checks:
        count=project_query_count(org,number,query)
        if count<minimum:
            failures.append(f"Project query check {label!r} returned {count}; expected at least {minimum}")
        else:
            print(f"Verification query {label!r}: {count} item(s).")

    legacy_names={(f.get("name") or "").casefold() for f in fields}
    for legacy in ("PI","Sprint"):
        if legacy.casefold() in legacy_names:
            warnings.append(f"Legacy compatibility field {legacy!r} remains; retain until values are audited against canonical fields")

    for warning in warnings:
        print(f"NOTE: {warning}",file=sys.stderr)
    if failures:
        print("GitHub Project verification FAILED:",file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}",file=sys.stderr)
        return 1
    print(f"GitHub Project verification passed: {total_items} project items, {total_issues} repository issues, {len(REQUIRED_VIEWS)} required views, canonical fields/options present.")
    return 0


def complete(org:str, repo:str, number:int)->int:
    project=project_query(org,number)
    canonicalize_field_names(project)
    project=project_query(org,number)
    ensure_single_select_options(project,"Item Type",ITEM_TYPE_OPTIONS)
    project=project_query(org,number)
    ensure_single_select_options(project,"Lifecycle",LIFECYCLE_OPTIONS)
    ensure_views(org,number)
    return verify(org,repo,number)


def main()->int:
    if len(sys.argv)!=5:
        print("usage: configure-github-project.py ORG REPO PROJECT_NUMBER {options|views|verify|complete}",file=sys.stderr)
        return 2
    org,repo,raw_number,action=sys.argv[1:]
    number=int(raw_number)
    if action=="options":
        project=project_query(org,number)
        canonicalize_field_names(project)
        project=project_query(org,number)
        ensure_single_select_options(project,"Item Type",ITEM_TYPE_OPTIONS)
        project=project_query(org,number)
        ensure_single_select_options(project,"Lifecycle",LIFECYCLE_OPTIONS)
        return 0
    if action=="views":
        ensure_views(org,number)
        return 0
    if action=="verify":
        return verify(org,repo,number)
    if action=="complete":
        return complete(org,repo,number)
    print(f"unsupported action: {action}",file=sys.stderr)
    return 2


if __name__=="__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError,json.JSONDecodeError,ValueError) as exc:
        print(f"ERROR: {exc}",file=sys.stderr)
        raise SystemExit(1)
