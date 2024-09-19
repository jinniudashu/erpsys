import{_ as c}from"./BasicForm.vue_vue_type_script_setup_true_lang-AWVm3OzD.js";import"./BasicForm.vue_vue_type_style_index_0_lang-B-82cvr1.js";import"./componentMap-CJ_TbWqL.js";import{C as d,a as f}from"./entry/index-DHKmWnTz.js";import{P as _}from"./index-krA2-UF3.js";import{M as a,C as i}from"./index-Bc0iOJwY.js";import{d as g,Z as C,a8 as b,a9 as n,k as s,u as o,l as p}from"./vue-BjERyvPm.js";import"./FormItem.vue_vue_type_script_lang-D1XLkyvn.js";import"./helper-B9T23wyW.js";import"./antd-BmrhB3rb.js";import"./index-CYuRykA_.js";import"./useWindowSizeFn-lnOspIwt.js";import"./useFormItem-B4KjxddK.js";import"./RadioButtonGroup.vue_vue_type_script_setup_true_lang-D4AXfD-q.js";import"./index-DZ2C_gU3.js";import"./uuid-D0SLUWHI.js";import"./useSortable-CIhNlKZL.js";import"./download-LXVxZx-p.js";import"./base64Conver-bBv-IO2K.js";import"./index-DVA2My2L.js";import"./IconPicker.vue_vue_type_script_setup_true_lang-IVPsmNBC.js";import"./copyTextToClipboard-DUmgQPO1.js";import"./index-CgPsHdbL.js";import"./index-B7WC2rIQ.js";import"./useContentViewHeight-CMjpDyRM.js";import"./onMountedOrActivated-DcvTUt7V.js";const A=g({__name:"Editor",setup(h){const m=[{field:"title",component:"Input",label:"title",defaultValue:"标题",rules:[{required:!0}]},{field:"JSON",component:"Input",label:"JSON",defaultValue:`{
        "name":"BeJson",
        "url":"http://www.xxx.com",
        "page":88,
        "isNonProfit":true,"
        address:{ 
            "street":"科技园路.",
            "city":"江苏苏州",
            "country":"中国"
        },
}`,rules:[{required:!0,trigger:"blur"}],render:({model:e,field:t})=>p(i,{value:e[t],mode:a.JSON,onChange:r=>{e[t]=r},config:{tabSize:10}})},{field:"PYTHON",component:"Input",label:"PYTHON",defaultValue:`def functionname( parameters ):
   "函数_文档字符串"
   function_suite
   return [expression]`,rules:[{required:!0,trigger:"blur"}],render:({model:e,field:t})=>p(i,{value:e[t],mode:a.PYTHON,onChange:r=>{e[t]=r}})}],{createMessage:u}=f();function l(e){u.success("click search,values:"+JSON.stringify(e))}return(e,t)=>(C(),b(o(_),{title:"代码编辑器组件嵌入Form示例"},{default:n(()=>[s(o(d),{title:"代码编辑器组件"},{default:n(()=>[s(o(c),{labelWidth:100,schemas:m,actionColOptions:{span:24},baseColProps:{span:24},onSubmit:l})]),_:1})]),_:1}))}});export{A as default};
