<%namespace name="tw" module="tw2.core.mako_util"/>
<div>
<table ${tw.attrs(attrs=w.attrs)}></table>
% if w.pager_id:
	<div id="${w.pager_id}"></div>
% endif
<script type="text/javascript">
$(document).ready(
    function(){
        var opts = ${w.options};
        var grid = $("#${w.selector}");
        grid.jqGrid(opts);
        if ( 'pager' in opts ) {
            opts['pager_selector'] = opts['pager'];
            opts['pager'] = $(opts['pager'])
            var pager_opts = ${w.pager_options}


            var prmEdit = ${w.prmEdit};
            var prmAdd = ${w.prmAdd};
            var prmDel = ${w.prmDel};
            var prmSearch = ${w.prmSearch};
            var prmView  = ${w.prmView};

            grid.navGrid('#'+opts['pager_selector'], pager_opts,
                         prmEdit, prmAdd, prmDel, prmSearch, prmView)
            % for btn in w.custom_pager_buttons:
                .navButtonAdd('#'+opts['pager_selector'], ${btn})
            % endfor

        }
		% if w._prmFilter:
		var prmFilter = ${w.prmFilter};
		grid.jqGrid('filterToolbar', prmFilter);
		% endif
    }
);
</script>
</div>
