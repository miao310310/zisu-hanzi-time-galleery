export const scripts = [
  {
    name: '甲骨文', era: '商代', glyph: '古', title: '契刻成文',
    description: '以刀代笔，线条质朴，保留着鲜明的象形意趣。',
    poster: '/images/script-gallery/oracle-poster.jpg',
    works: [
      { title: '殷墟甲骨卜辞拓片', caption: '从分布、转折与字内空间，观察契刻留下的节奏。', image: '/images/script-gallery/oracle-01.jpg' },
      { title: '《祭祀狩猎涂朱牛骨刻辞》', caption: '可留意刻辞与材料表面之间的关系。', image: '/images/script-gallery/oracle-02.jpg' },
      { title: '完整刻辞龟甲（正面）', caption: '试着先看整体布局，再辨认局部线条。', image: '/images/script-gallery/oracle-03.jpg' }
    ]
  },
  {
    name: '金文', era: '商周', glyph: '鼎', title: '铸铜铭史',
    description: '铸刻于青铜器上的文字，形态凝重，气息古厚。',
    poster: '/images/script-gallery/bronze-poster.jpg',
    works: [
      { title: '西周《毛公鼎》铭文拓片', caption: '观察线条的厚重感，以及字与字之间的呼应。', image: '/images/script-gallery/bronze-01.jpg' },
      { title: '西周《散氏盘》铭文拓片', caption: '从结体的开合与行列关系进入阅读。', image: '/images/script-gallery/bronze-02.jpg' },
      { title: '西周《何尊》铭文拓片', caption: '比较单字细节与整段铭文的排布。', image: '/images/script-gallery/bronze-03.jpg' }
    ]
  },
  {
    name: '小篆', era: '秦代', glyph: '篆', title: '婉转匀整',
    description: '线条圆转均匀，结构修长，展现秩序之美。',
    poster: '/images/script-gallery/seal-poster.jpg',
    works: [
      { title: '秦《峄山碑》小篆', caption: '从长宽比例与中轴关系感受匀整。', image: '/images/script-gallery/seal-01.jpg' },
      { title: '《泰山刻石》原石', caption: '观察线条圆转与石刻材质带来的视觉差异。', image: '/images/script-gallery/seal-02.jpg' },
      { title: '秦二世诏版铭文拓片', caption: '比较小篆在不同载体上的布局与节奏。', image: '/images/script-gallery/seal-03.jpg' }
    ]
  },
  {
    name: '隶书', era: '汉代', glyph: '隶', title: '蚕头雁尾',
    description: '形体趋于扁平，横向舒展，书写更为便捷。',
    poster: '/images/script-gallery/clerical-poster.jpg',
    works: [
      { title: '东汉《曹全碑》拓片（局部）', caption: '留意横向展开的重心与笔画的舒展。', image: '/images/script-gallery/clerical-01.jpg' },
      { title: '东汉《张迁碑》拓片（局部）', caption: '可比较转折、收笔和字形的力量感。', image: '/images/script-gallery/clerical-02.jpg' },
      { title: '东汉《礼器碑》拓片（局部）', caption: '从主笔与留白，观察隶书的节奏。', image: '/images/script-gallery/clerical-03.jpg' }
    ]
  },
  {
    name: '楷书', era: '魏晋以后', glyph: '永', title: '点画有度',
    description: '笔画分明，结构端正，在法度中见风骨。',
    poster: '/images/script-gallery/regular-poster.jpg',
    works: [
      { title: '唐·颜真卿《多宝塔碑》拓片（局部）', caption: '先找重心，再看点画之间的距离与呼应。', image: '/images/script-gallery/regular-01.jpg' },
      { title: '唐·柳公权《玄秘塔碑》拓片（局部）', caption: '观察线条的提按变化与结构的紧密程度。', image: '/images/script-gallery/regular-02.jpg' },
      { title: '唐·欧阳询《九成宫醴泉铭》拓片（局部）', caption: '从笔画长短和留白关系理解法度。', image: '/images/script-gallery/regular-03.jpg' }
    ]
  },
  {
    name: '行草', era: '汉晋以来', glyph: '行', title: '笔势流转',
    description: '行书与草书各具特点，笔势连贯，变化丰富。',
    poster: '/images/script-gallery/running-poster.jpg',
    works: [
      { title: '东晋·王羲之《兰亭序》', caption: '沿着笔势走向，感受字与字之间的连贯。', image: '/images/script-gallery/running-01.jpg' },
      { title: '唐·颜真卿《祭侄文稿》', caption: '观察行列、墨色与节奏如何共同表达情绪。', image: '/images/script-gallery/running-02.jpg' },
      { title: '宋·苏轼《黄州寒食诗帖》', caption: '从疏密、停顿和连笔关系进入作品。', image: '/images/script-gallery/running-03.jpg' }
    ]
  }
];
export const characters=Object.entries({日:'早期字形具有象形特点，以轮廓和内部标记表现太阳。',山:'早期字形表现山峰高低起伏的轮廓。',水:'早期字形以流动的线条表现水流。',木:'早期字形具有树木的形象：上部似枝，下部似根。'}).map(([character,description])=>({id:character,character,description,sources:[]}));
export const questions=[{q:'哪种字体通常线条圆转均匀、结构修长？',options:['小篆','楷书','行草'],answer:0,explanation:'小篆强调线条的匀整与圆转。'},{q:'“山”的早期字形主要表现什么？',options:['水流','山峰轮廓','树木枝干'],answer:1,explanation:'山字具有山峰轮廓的象形意味。'},{q:'临写前应该先观察什么？',options:['书写速度','字的颜色','重心、比例与留白'],answer:2,explanation:'先观察整体结构，再落笔。'}];
