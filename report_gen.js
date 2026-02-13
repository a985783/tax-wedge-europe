const { 
    Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, 
    AlignmentType, HeadingLevel, WidthType, ShadingType, BorderStyle, 
    LevelFormat, PageNumber, Header, Footer, PageBreak
} = require('docx');
const fs = require('fs');

const tableBorder = { style: BorderStyle.SINGLE, size: 1, color: "000000" };
const cellBorders = { top: tableBorder, bottom: tableBorder, left: tableBorder, right: tableBorder };

const doc = new Document({
    styles: {
        default: {
            document: {
                run: { font: "Arial", size: 22 }
            }
        },
        paragraphStyles: [
            {
                id: "Title",
                name: "Title",
                basedOn: "Normal",
                run: { size: 48, bold: true, color: "000000", font: "Arial" },
                paragraph: { spacing: { before: 240, after: 120 }, alignment: AlignmentType.CENTER }
            },
            {
                id: "Heading1",
                name: "Heading 1",
                basedOn: "Normal",
                next: "Normal",
                quickFormat: true,
                run: { size: 32, bold: true, color: "000000", font: "Arial" },
                paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 0 }
            },
            {
                id: "Heading2",
                name: "Heading 2",
                basedOn: "Normal",
                next: "Normal",
                quickFormat: true,
                run: { size: 28, bold: true, color: "000000", font: "Arial" },
                paragraph: { spacing: { before: 180, after: 120 }, outlineLevel: 1 }
            }
        ]
    },
    numbering: {
        config: [
            {
                reference: "bullet-list",
                levels: [{
                    level: 0,
                    format: LevelFormat.BULLET,
                    text: "•",
                    alignment: AlignmentType.LEFT,
                    style: { paragraph: { indent: { left: 720, hanging: 360 } } }
                }]
            },
            {
                reference: "numbered-list",
                levels: [{
                    level: 0,
                    format: LevelFormat.DECIMAL,
                    text: "%1.",
                    alignment: AlignmentType.LEFT,
                    style: { paragraph: { indent: { left: 720, hanging: 360 } } }
                }]
            }
        ]
    },
    sections: [{
        properties: {
            page: {
                margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
            }
        },
        headers: {
            default: new Header({
                children: [
                    new Paragraph({
                        alignment: AlignmentType.RIGHT,
                        children: [new TextRun({ text: "学术含金量与学术规范综合分析报告", color: "666666", size: 18 })]
                    })
                ]
            })
        },
        footers: {
            default: new Footer({
                children: [
                    new Paragraph({
                        alignment: AlignmentType.CENTER,
                        children: [
                            new TextRun("第 "),
                            new TextRun({ children: [PageNumber.CURRENT] }),
                            new TextRun(" 页，共 "),
                            new TextRun({ children: [PageNumber.TOTAL_PAGES] }),
                            new TextRun(" 页")
                        ]
                    })
                ]
            })
        },
        children: [
            new Paragraph({
                heading: HeadingLevel.TITLE,
                children: [new TextRun("论文学术含金量与学术规范综合分析报告")]
            }),
            new Paragraph({
                alignment: AlignmentType.CENTER,
                children: [new TextRun({ text: "评估对象：关于欧洲间接税传导与价格刚性的研究", italics: true })]
            }),
            new Paragraph({ spacing: { after: 400 } }),

            new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("1. 执行摘要")] }),
            new Paragraph({
                children: [new TextRun({ text: "总体评分：7.7 / 10", bold: true, size: 28 })]
            }),
            new Paragraph({
                children: [new TextRun("本报告对该论文的理论基础、方法论、学术规范及可复制性进行了全面评估。论文在理论对话和计量识别策略上表现优异，但在数据一致性、代码管理和可复制性方面存在显著风险。")]
            }),
            new Paragraph({ spacing: { before: 200 }, children: [new TextRun({ text: "核心优势：", bold: true })] }),
            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun("理论对话深入：直接回应 Benzarti 等 (AER, 2020) 的核心发现，具有极高的学术起点。")]
            }),
            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun("识别策略先进：采用 Stacked Event Study 规避了传统 TWFE 模型在异质性处理效应下的负权重问题。")]
            }),
            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun("统计推断严谨：针对小样本聚类（30个国家）采用了 Wild Cluster Bootstrap 进行校正。")]
            }),
            new Paragraph({ spacing: { before: 200 }, children: [new TextRun({ text: "主要风险：", bold: true })] }),
            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun("数据一致性危机：正文描述系数 (0.35) 与实证结果文件 (0.43) 存在严重不匹配。")]
            }),
            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun("预趋势显著性：t=-2 处的显著性暗示存在预期效应，可能挑战因果识别的排他性约束。")]
            }),
            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun("工程化水平低下：缺乏版本控制（Git）和依赖锁定，代码维护成本极高，可复制性评分偏低。")]
            }),

            new Paragraph({ children: [new PageBreak()] }),

            new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("2. 学术含金量评估")] }),
            
            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.1 理论贡献与创新")] }),
            new Paragraph({
                children: [new TextRun("论文构建了基于菜单成本与不完全竞争的理论框架，深入探讨了间接税（Tax Wedge）向消费者价格传导的机制。其核心学术价值在于对 Benzarti 等 (2020) 关于传导不对称性结论的挑战与细化。通过引入高频识别传统，论文在理论层面上为价格刚性提供了更具动态性的解释。")]
            }),

            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.2 方法论突破")] }),
            new Paragraph({
                children: [new TextRun("在计量经济学方法上，论文紧跟前沿，采用了 Stacked Event Study 设计。这一设计有效解决了在交错实施（Staggered Adoption）背景下，传统双向固定效应模型可能产生的偏误。此外，Tax Wedge 的代数识别过程逻辑严密，确保了政策变动捕捉的纯净度。")]
            }),

            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.3 实证发现的价值")] }),
            new Paragraph({
                children: [new TextRun("实证结果显示，虽然传导是不完全的，但在对称性上表现出较强的解释力。这一发现对于欧洲各国的增值税政策制定具有直接的参考意义，特别是在评估税率调整对通胀影响的预测方面。")]
            }),

            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.4 学术影响力预测")] }),
            new Paragraph({
                children: [new TextRun("鉴于其研究问题的政策相关性和方法论的严谨性，该论文具备在国际一流经济学期刊（如 Journal of Public Economics 或 European Economic Review）发表的潜力。若能解决预趋势和数据一致性问题，其引用潜力巨大。")]
            }),

            new Paragraph({ children: [new PageBreak()] }),

            new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("3. 学术规范审查")] }),

            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.1 写作规范达标情况")] }),
            new Paragraph({
                children: [new TextRun("论文结构完整，逻辑清晰。然而，在细节描述上存在严重偏差：")]
            }),
            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun("核心系数矛盾：正文宣称 0.35，而 results_main.md 显示为 0.43。")]
            }),
            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun("异质性描述错误：对 Periphery 地区的描述与实际统计结果（t=0 时不显著，t=12 时显著）完全相反。")]
            }),

            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.2 数据透明度与可复制性")] }),
            new Paragraph({
                children: [new TextRun("数据来源透明，提供了完整的复现包。但可复制性评分仅为 5.8/10，主要原因包括：")]
            }),
            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun("缺乏版本控制：未发现 .git 目录，这在现代学术研究中属于重大管理缺失。")]
            }),
            new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun("文档不一致：README 中的操作步骤与实际脚本逻辑存在脱节。")]
            }),

            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.3 引用和学术诚信")] }),
            new Paragraph({
                children: [new TextRun("引用详实，对话前沿。但需注意缺失“利益冲突声明”，这在顶级期刊投稿中是必填项。")]
            }),

            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.4 图表和统计规范")] }),
            new Paragraph({
                children: [new TextRun("图表制作专业，但存在统计显著性标注不一致的问题。Markdown 与 LaTeX 混用导致部分标签未正常渲染，影响了阅读体验。")]
            }),

            new Paragraph({ children: [new PageBreak()] }),

            new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("4. 计量经济学方法评估")] }),

            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("4.1 识别策略有效性")] }),
            new Paragraph({
                children: [new TextRun("Stacked Event Study 的应用是本文的一大亮点。通过构建“清洁”的对照组，论文成功排除了已处理单位作为对照组带来的污染。")]
            }),

            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("4.2 估计方法的适当性")] }),
            new Paragraph({
                children: [new TextRun("考虑到聚类数量（30个国家）不足 50 个，论文正确地采用了 Wild Cluster Bootstrap 进行推断。这种方法在小样本聚类情况下比传统的聚类稳健标准误更具保守性和可靠性。")]
            }),

            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("4.3 统计推断的严谨性")] }),
            new Paragraph({
                children: [new TextRun("代码实现了基于 Cameron 等 (2008) 的算法，重复次数达 9999 次，种子设定为 42，确保了结果的可重复性。但在 Webb_6pt 的实现上存在微小瑕疵（实际为 4 点实现）。")]
            }),

            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("4.4 稳健性检验充分性")] }),
            new Paragraph({
                children: [new TextRun("论文包含了安慰剂检验（时间置换）和亚组分析。然而，亚组分类规则存在硬编码现象，且部分稳健性检验结果未在文档中系统性呈现。")]
            }),

            new Paragraph({ children: [new PageBreak()] }),

            new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("5. 关键问题清单")] }),

            new Table({
                columnWidths: [2000, 7360],
                rows: [
                    new TableRow({
                        tableHeader: true,
                        children: [
                            new TableCell({
                                borders: cellBorders,
                                shading: { fill: "E6E6E6", type: ShadingType.CLEAR },
                                children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "级别", bold: true })] })]
                            }),
                            new TableCell({
                                borders: cellBorders,
                                shading: { fill: "E6E6E6", type: ShadingType.CLEAR },
                                children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "问题描述", bold: true })] })]
                            })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "严重", color: "FF0000", bold: true })] })] }),
                            new TableCell({ borders: cellBorders, children: [
                                new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("正文系数 (0.35) 与结果文件 (0.43) 不一致。")] }),
                                new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("t=-2 预趋势显著，挑战平行趋势假设。")] }),
                                new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Periphery 地区实证结果描述与数据完全相反。")] })
                            ] })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "中等", color: "FF6600", bold: true })] })] }),
                            new TableCell({ borders: cellBorders, children: [
                                new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("代码库缺乏 Git 版本控制。")] }),
                                new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("models.py 冗长且存在大量重复代码。")] }),
                                new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("缺失利益冲突声明。")] })
                            ] })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "小问题", color: "0000FF", bold: true })] })] }),
                            new TableCell({ borders: cellBorders, children: [
                                new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Webb_6pt 权重分布实现为 4 点。")] }),
                                new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("LaTeX 标签渲染占位符问题。")] })
                            ] })
                        ]
                    })
                ]
            }),

            new Paragraph({ children: [new PageBreak()] }),

            new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("6. 改进建议")] }),

            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("6.1 短期可执行改进")] }),
            new Paragraph({
                numbering: { reference: "numbered-list", level: 0 },
                children: [new TextRun("对齐数据：重新核对所有回归输出，确保正文、图表与底层数据完全一致。")]
            }),
            new Paragraph({
                numbering: { reference: "numbered-list", level: 0 },
                children: [new TextRun("处理预趋势：探讨 t=-2 显著的原因（如政策预期），或尝试更严格的样本筛选。")]
            }),
            new Paragraph({
                numbering: { reference: "numbered-list", level: 0 },
                children: [new TextRun("完善声明：添加利益冲突声明和数据可用性说明。")]
            }),

            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("6.2 长期系统性改进")] }),
            new Paragraph({
                numbering: { reference: "numbered-list", level: 0 },
                children: [new TextRun("引入 Git：建立版本控制系统，记录研究过程中的每一次重大调整。")]
            }),
            new Paragraph({
                numbering: { reference: "numbered-list", level: 0 },
                children: [new TextRun("重构代码：将 models.py 模块化，消除重复逻辑，提高代码的可维护性。")]
            }),
            new Paragraph({
                numbering: { reference: "numbered-list", level: 0 },
                children: [new TextRun("自动化文档：建立独立的数据字典和审计协议，确保元数据匹配的自动化。")]
            }),

            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("6.3 期刊投稿建议")] }),
            new Paragraph({
                children: [new TextRun("首选目标：Journal of Public Economics, American Economic Journal: Economic Policy。")]
            }),
            new Paragraph({
                children: [new TextRun("备选目标：European Economic Review, Journal of Applied Econometrics。")]
            }),

            new Paragraph({ children: [new PageBreak()] }),

            new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("7. 附录：评分卡")] }),

            new Table({
                columnWidths: [4000, 2000, 3360],
                rows: [
                    new TableRow({
                        tableHeader: true,
                        children: [
                            new TableCell({ borders: cellBorders, shading: { fill: "E6E6E6", type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "评估维度", bold: true })] })] }),
                            new TableCell({ borders: cellBorders, shading: { fill: "E6E6E6", type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "得分", bold: true })] })] }),
                            new TableCell({ borders: cellBorders, shading: { fill: "E6E6E6", type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "顶级期刊标准对比", bold: true })] })] })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("理论基础和创新性")] })] }),
                            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("8.3")] })] }),
                            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("达标 (AER/JPE 级别)")] })] })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("学术规范和写作质量")] })] }),
                            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("8.5")] })] }),
                            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("基本达标，需修正偏差")] })] })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("可复制性和数据完整性")] })] }),
                            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("5.8")] })] }),
                            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("低于标准，需重大改进")] })] })
                        ]
                    }),
                    new TableRow({
                        children: [
                            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("计量经济学方法")] })] }),
                            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("8.2")] })] }),
                            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("优秀，符合前沿规范")] })] })
                        ]
                    })
                ]
            }),
            new Paragraph({ spacing: { before: 400 }, children: [new TextRun({ text: "报告生成日期：2026年2月14日", italics: true })] }),
            new Paragraph({ children: [new TextRun({ text: "评估机构：Antigravity Academic Review Team", italics: true })] })
        ]
    }]
});

Packer.toBuffer(doc).then((buffer) => {
    fs.writeFileSync("/Users/cuiqingsong/Documents/论文 3/academic_analysis_report.docx", buffer);
    console.log("Report generated successfully at /Users/cuiqingsong/Documents/论文 3/academic_analysis_report.docx");
});
