<%namespace name="tw" module="tw2.core.mako_util"/>
<div>
<table ${tw.attrs(attrs=w.attrs)}></table>
% if 'pager' in w.options:
	<div id="${w.options['pager']}"></div>
% endif
<script type="text/javascript">
$(document).ready(
    function(){
        var opts = ${w._options};
        var grid = $("#${w.attrs['id']}");
        grid.jqGrid(opts);
        if ( 'pager' in opts ) {
            opts['pager_selector'] = opts['pager'];
            opts['pager'] = $(opts['pager'])
            var pager_opts = ${w._pager_options}
            grid.navGrid('#'+opts['pager_selector'], pager_opts);
        }
    }
);
</script>
</div>
