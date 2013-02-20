<%namespace name="tw" module="tw2.core.mako_util"/>
<div>
<table ${tw.attrs(attrs=w.attrs)}></table>
% if w.pager_id:
    <div id="${w.pager_id}"></div>
% endif
<script type="text/javascript">
$(document).ready(
    function(){
        var opts = ${w.options | n};
        var grid = $("#${w.selector}");
        grid.jqGrid(opts);
        if ( 'pager' in opts ) {
            opts['pager_selector'] = opts['pager'];
            opts['pager'] = $(opts['pager'])
            var pager_opts = ${w._pager_options | n}
            var prmEdit = ${w._prmEdit | n};
            var prmAdd = ${w._prmAdd | n};
            var prmDel = ${w._prmDel | n};
            var prmSearch = ${w._prmSearch | n};
            var prmView  = ${w._prmView | n};
            grid.navGrid('#'+opts['pager_selector'], pager_opts,
                         prmEdit, prmAdd, prmDel, prmSearch, prmView)
            % for btn in w._custom_pager_buttons:
                .navButtonAdd('#'+opts['pager_selector'], ${btn | n})
            % endfor
            ;
        }
        % if w.prmFilter:
        var prmFilter = ${w._prmFilter | n};
        grid.jqGrid('filterToolbar', prmFilter);
        % endif
    }
);
</script>
</div>
