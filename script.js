
const data = window.chartData || [];

// 세련된 고대비 색상 팔레트 정의
const customColors = [
    '#007AFF', '#34C759', '#FF9500', '#FF3B30', '#5856D6', 
    '#FFCC00', '#5AC8FA', '#FF2D55', '#AF52DE', '#4CD964'
];

Highcharts.chart('container', {
    chart: { height: '100%' },
    title: { text: '북한 의료 시설 분포 현황' },
    subtitle: { text: '데이터 출처: 북한 스마트폰 내부 DB' },

    // ✨ 핵심 수정 1: 차트의 기본 색상으로 위에서 정의한 팔레트를 사용합니다.
    colors: customColors,

    series: [{
        type: 'sunburst',
        data: data,
        name: 'Root',
        allowDrillToNode: true,
        cursor: 'pointer',
        dataLabels: { format: '{point.name}' },

        // ✨ 핵심 수정 2: 복잡한 옵션을 제거하고, 각 레벨별 색상 규칙을 명확하게 정의합니다.
        levels: [{
            level: 1,
            // 중앙 원은 투명하게 설정
            color: 'transparent'
        }, {
            level: 2,
            // 레벨 2 항목들은 팔레트의 색상을 순서대로 부여받습니다.
            colorByPoint: true
        }, {
            level: 3,
            // 레벨 3 항목들도 부모 색상과 상관없이, 팔레트의 색상을 다시 순서대로 부여받습니다.
            colorByPoint: true
        }, {
            level: 4,
            // 레벨 4 항목들도 마찬가지입니다.
            colorByPoint: true
        }]
    }],
    tooltip: {
        formatter: function () {
            const point = this.point;
            let tooltipText = `<b>${point.name}</b>`;
            if (point.value) {
                tooltipText += `<br><hr style="border-top: 1px solid #ccc; margin: 5px 0;">`;
                if (point.options.description) {
                    tooltipText += `<b>설명:</b> ${point.options.description}<br>`;
                }
                if (point.options.nearby_facilities) {
                    tooltipText += `<b>인근시설:</b> ${point.options.nearby_facilities}`;
                }
            } 
            else if (point.val !== undefined) {
                const totalCountText = (point.options.id === 'root') ? '전체 시설 총 개수' : '하위 시설 총 개수';
                tooltipText += `<br>${totalCountText}: ${point.val}`;
            }
            return tooltipText;
        }
    }
});
