<%namespace name="tw" module="tw2.core.mako_util"/>\
<table ${tw.attrs(attrs=w.attrs)}>
</table>
% if w.paginate:
<div id=${w._pager}></div>
% endif
<script type="text/javascript">
    //Code to gridify the above table and paginator
    var ${w.attrs['id']}_options = { url: ${w._url}, pager: ${w._pager} };
    jQuery.extend(${w.attrs['id']}_options, ${w._options});
    jQuery(document).ready(
      function(){ 
        jQuery("#${w.attrs['id']}").jqGrid(${w.attrs['id']}_options);
    % if w._pager_options:
        jQuery("#${w.attrs['id']}").jqGrid('navGrid', '#' + ${w._pager},
            ${w._pager_options.get('options', "null")},
            ${w._pager_options.get('pEdit', "null")},
            ${w._pager_options.get('pAdd', "null")},
            ${w._pager_options.get('pSearch', "null")});
    % endif
      }); 
</script>
