// ===== تحسينات شريط التنقل السفلي =====

// ضمان ثبات شريط التنقل السفلي
document.addEventListener('DOMContentLoaded', function() {
  const bottomNav = document.querySelector('.mobile-bottom-nav');
  
  if (bottomNav) {
    // إضافة خصائص إضافية لضمان الثبات
    bottomNav.style.position = 'fixed';
    bottomNav.style.bottom = '0';
    bottomNav.style.left = '0';
    bottomNav.style.right = '0';
    bottomNav.style.width = '100%';
    bottomNav.style.zIndex = '9999';
    bottomNav.style.transform = 'translateZ(0)';
    bottomNav.style.webkitTransform = 'translateZ(0)';
    bottomNav.style.willChange = 'transform';
    bottomNav.style.webkitBackfaceVisibility = 'hidden';
    bottomNav.style.backfaceVisibility = 'hidden';
    
    // إضافة padding-bottom للجسم
    document.body.style.paddingBottom = '70px';
    
    // إضافة margin-bottom للفوتر
    const footer = document.querySelector('.main-footer');
    if (footer) {
      footer.style.marginBottom = '70px';
    }
  }
});

// تحسين التمرير لضمان عدم تأثر شريط التنقل السفلي
window.addEventListener('scroll', function() {
  const bottomNav = document.querySelector('.mobile-bottom-nav');
  
  if (bottomNav) {
    // ضمان ثبات الشريط
    bottomNav.style.position = 'fixed';
    bottomNav.style.bottom = '0';
    bottomNav.style.left = '0';
    bottomNav.style.right = '0';
    bottomNav.style.width = '100%';
    bottomNav.style.zIndex = '9999';
  }
});

// تحسين الاستجابة لللمس
document.addEventListener('touchstart', function(e) {
  if (e.target.closest('.mobile-bottom-nav .nav-item')) {
    e.target.closest('.mobile-bottom-nav .nav-item').style.transform = 'scale(0.95)';
  }
});

document.addEventListener('touchend', function(e) {
  if (e.target.closest('.mobile-bottom-nav .nav-item')) {
    setTimeout(() => {
      e.target.closest('.mobile-bottom-nav .nav-item').style.transform = 'scale(1)';
    }, 150);
  }
});

// تحسين الأداء
window.addEventListener('resize', function() {
  const bottomNav = document.querySelector('.mobile-bottom-nav');
  
  if (bottomNav && window.innerWidth <= 1024) {
    bottomNav.style.display = 'flex';
  } else if (bottomNav && window.innerWidth > 1024) {
    bottomNav.style.display = 'none';
  }
});
