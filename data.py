import pandas as pd
import json

# -------------------------------------------------------------------
# Step 1: 엑셀 파일 읽기 (이전과 동일)
# -------------------------------------------------------------------
try:
    df = pd.read_excel('data.xlsx', sheet_name='1')
    if '설명' not in df.columns:
        df['설명'] = '상세 설명 없음'
    print("✅ 'data.xlsx' 파일을 성공적으로 불러왔습니다.")
except FileNotFoundError:
    print("❌ 'data.xlsx' 파일을 찾을 수 없습니다.")
    df = None
except Exception as e:
    print(f"파일을 읽는 중 오류가 발생했습니다: {e}")
    df = None

# -------------------------------------------------------------------
# Step 2: Pandas 데이터를 Highcharts용 데이터 형식으로 변환 (이전과 동일)
# -------------------------------------------------------------------
if df is not None and not df.empty:

    highcharts_data = [{'id': 'root', 'parent': '', 'name': '전체 시설'}]
    added_ids = {'root'}
    path_cols = ['카테고리', '시', '군', '이름']
    info_cols = ['인근시설', '설명']
    df[path_cols + info_cols] = df[path_cols + info_cols].fillna('')

    for _, row in df.iterrows():
        parent_id = 'root'
        for i, col in enumerate(path_cols):
            name = row[col]
            if not name:
                continue
            current_id = f"{parent_id}/{name}"
            if current_id not in added_ids:
                node = {'id': current_id, 'parent': parent_id, 'name': str(name)}
                if i == len(path_cols) - 1:
                    node['value'] = 1
                    node['description'] = str(row['설명'])
                    node['nearby_facilities'] = str(row['인근시설'])
                highcharts_data.append(node)
                added_ids.add(current_id)
            parent_id = current_id

    json_string = json.dumps(highcharts_data, indent=2, ensure_ascii=False)
    print("\n✅ Highcharts용 데이터 생성을 완료했습니다.")

    # -------------------------------------------------------------------
    # Step 3: 분리된 파일 생성 (JS 로직 최종 수정)
    # -------------------------------------------------------------------

    css_content = """
body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
.highcharts-figure, .highcharts-data-table table { min-width: 320px; max-width: 800px; margin: 1em auto; }
#container { height: 800px; }
"""

    js_content = """
const data = window.chartData || [];

// 세련된 고대비 색상 팔레트 정의
const customColors = [
    '#007AFF', '#34C759', '#FF9500', '#FF3B30', '#5856D6', 
    '#FFCC00', '#5AC8FA', '#FF2D55', '#AF52DE', '#4CD964'
];

Highcharts.chart('container', {
    chart: { height: '100%' },
    title: { text: '의료 시설 분포 현황' },
    subtitle: { text: '데이터 출처: data.xlsx' },

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
"""

    html_template = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>Highcharts Sunburst (Final Version)</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <script src="https://code.highcharts.com/highcharts.js"></script>
    <script src="https://code.highcharts.com/modules/sunburst.js"></script>
    <script src="https://code.highcharts.com/modules/exporting.js"></script>
    <script src="https://code.highcharts.com/modules/export-data.js"></script>
    <script src="https://code.highcharts.com/modules/accessibility.js"></script>

    <figure class="highcharts-figure">
      <div id="container"></div>
    </figure>

    <script>
        window.chartData = {json_string};
    </script>

    <script src="script.js" defer></script>
</body>
</html>
"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_template)
    with open("style.css", "w", encoding="utf-8") as f:
        f.write(css_content)
    with open("script.js", "w", encoding="utf-8") as f:
        f.write(js_content)

    print("\n✅ 최종 수정된 'index.html', 'style.css', 'script.js' 파일이 성공적으로 생성되었습니다!")

else:
    print("\n데이터가 없어 차트를 생성하지 못했습니다.")